"""Cheap source/API checks before invoking the expensive full Telegram build."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import plistlib
import os
import python_support
import python_support_smoke


def contract_errors(source, path=''):
    errors = []
    if re.search(r'textAlertController\s*\(\s*context:', source) and 'import PresentationDataUtils' not in source:
        errors.append('textAlertController(context:) requires PresentationDataUtils')
    # TextFormat's own sources declare these functions and cannot import their module.
    if 'stringWithAppliedEntities(' in source and 'import TextFormat' not in source and not path.startswith('submodules/TextFormat/'):
        errors.append('stringWithAppliedEntities requires TextFormat')
    if re.search(r'\.fullgramVisibleMessageReactions(?:AndPeers)?\s*\(', source) and 'import AccountContext' not in source:
        errors.append('Full Gram reaction display helpers require AccountContext')
    if path.endswith('ChatListControllerNode.swift') and re.search(r'!\s*self\.isSearchDisplayControllerActive\b', source):
        errors.append('ChatListControllerNode.isSearchDisplayControllerActive is ActiveSearch?; compare it with nil')
    if path.rsplit('/', 1)[-1].startswith('FullGram') and re.search(r'\.(?:content|title|image)EdgeInsets\b', source):
        errors.append('UIButton edge insets are deprecated in iOS 15; use UIButton.Configuration.contentInsets')
    if path.rsplit('/', 1)[-1].startswith('FullGram') and re.search(r'\b(?:add|remove|set)TemporaryAttributes?\b', source):
        errors.append('NSLayoutManager temporary attributes are macOS-only; draw a separate text layout on iOS')
    return errors


def reaction_dependency_errors(source_file):
    text = source_file.read_text(encoding='utf-8')
    if not re.search(r'\.fullgramVisibleMessageReactions(?:AndPeers)?\s*\(', text):
        return []
    for parent in source_file.parents:
        build = parent / 'BUILD'
        if build.is_file():
            if '//submodules/AccountContext' not in build.read_text(encoding='utf-8'):
                return ['Full Gram reaction display helpers require a direct AccountContext Bazel dependency']
            return []
    return ['No BUILD file found for Full Gram reaction display helpers']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    import_check = source / "build-system/Make/PostboxImportCheck.py"
    if import_check.exists():
        subprocess.run([sys.executable, str(import_check), str(source)], check=True)
        print("PASS: actual upstream Postbox import/access check before native dependencies")
    paths = set()
    for arguments in (['diff', '--name-only', '-z', 'HEAD'], ['ls-files', '--others', '--exclude-standard', '-z']):
        output = subprocess.check_output(['git', *arguments], cwd=source)
        paths.update(path.decode('utf-8') for path in output.split(b'\0') if path.endswith(b'.swift'))
    errors = []
    for path in sorted(paths):
        for error in contract_errors((source / path).read_text(encoding='utf-8'), path):
            errors.append(f'{path}: {error}')
        for error in reaction_dependency_errors(source / path):
            errors.append(f'{path}: {error}')
    scheme = (source / 'submodules/TelegramApi/swift_scheme.tl').read_text(encoding='utf-8')
    for method in ('sendMessage', 'sendMedia', 'sendMultiMedia', 'forwardMessages'):
        line = next((line for line in scheme.splitlines() if line.startswith(f'messages.{method}#')), '')
        if 'silent:flags.5?true' not in line:
            errors.append(f'Telegram API silent flag changed for messages.{method}')

    def parse(path):
        result = subprocess.run(['xcrun', 'swiftc', '-frontend', '-parse', str(source / path)], capture_output=True, text=True)
        return result.returncode, result.stdout + result.stderr

    with ThreadPoolExecutor(max_workers=2) as executor:
        for path, (code, output) in zip(sorted(paths), executor.map(parse, sorted(paths))):
            if code:
                errors.append(f'{path}:\n{output}')
    bridge = source / 'submodules/FullGramPythonBridge/Sources/FullGramPythonBridgeObjC.m'
    if bridge.exists():
        cache = Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'fullgram-python-support'
        python_support.prepare(source, cache, 'debug_sim_arm64')
        python_sdk = subprocess.check_output(['xcrun', '--sdk', 'iphonesimulator', '--show-sdk-path'], text=True).strip()
        result = subprocess.run(['xcrun', 'clang', '-fsyntax-only', '-fobjc-arc', '-fmodules', '-Werror',
                                 '-isysroot', python_sdk, '-target', 'arm64-apple-ios15.0-simulator',
                                 '-F', str(source / 'third-party/fullgram-python'), str(bridge)], capture_output=True, text=True)
        if result.returncode:
            errors.append(f'Actual CPython Objective-C SDK check:\n{result.stdout}{result.stderr}')
        else:
            print('PASS: real CPython bridge checked against the pinned Python and iOS Simulator headers')
            python_support_smoke.run(source, cache, Path(__file__).resolve().parents[1] / 'runtime')

    # These standalone sources use SDK frameworks only. Type-check their actual
    # implementations before the expensive full Telegram build.
    sdk_sources = [source / 'submodules/TelegramUI/Sources' / name for name in (
        'Chat/FullGramMessageShotCanvas.swift', 'FullGramStartupStorage.swift', 'FullGramStartupFailureController.swift')]
    sdk_sources.append(source / 'submodules/TelegramUI/Sources/FullGramMusicHaptics.swift')
    sdk_sources.append(source / 'submodules/TelegramUI/Sources/FullGramLyricsLineLabel.swift')
    sdk_sources.append(source / 'submodules/TelegramUI/Sources/FullGramLyricsPauseView.swift')
    sdk_sources.append(source / 'submodules/Display/Source/FullGramPetpetController.swift')
    sdk_sources.append(source / 'submodules/Display/Source/FullGramPluginAvatar.swift')
    sdk_sources.append(source / 'submodules/Display/Source/FullGramArcadeGameController.swift')
    sdk_sources.append(source / 'submodules/Display/Source/FullGramChatColorPickerController.swift')
    sdk_sources.append(source / 'submodules/TelegramPresentationData/Sources/FullGramAppIconCatalog.swift')
    sdk_sources.extend(source / 'submodules/SettingsUI/Sources' / name for name in (
        'FullGramPreferencesHubController.swift', 'FullGramAppIconPickerController.swift'))
    if any(path.exists() for path in sdk_sources):
        sdk = subprocess.check_output(['xcrun', '--sdk', 'iphonesimulator', '--show-sdk-path'], text=True).strip()
        for path in sdk_sources:
            if not path.exists():
                continue
            companions = [path.with_name('FullGramMusicHapticsTimeline.swift')] if path.name == 'FullGramMusicHaptics.swift' else []
            if path.name == 'FullGramLyricsLineLabel.swift':
                companions = [path.with_name(name) for name in ('FullGramLyricsTiming.swift', 'FullGramLyricsYaml.swift')]
                companions.append(source / 'submodules/Display/Source/FullGramPlayerTextStyle.swift')
            result = subprocess.run(['xcrun', 'swiftc', '-typecheck', '-swift-version', '5', '-warnings-as-errors',
                                     '-sdk', sdk, '-target', 'arm64-apple-ios15.0-simulator', str(path),
                                     *map(str, companions)], capture_output=True, text=True)
            if result.returncode:
                errors.append(f'{path.name} SDK type check:\n{result.stdout}{result.stderr}')
            else:
                print(f'PASS: actual {path.name} type-checked against the iOS Simulator SDK')
        # Model-only harness from real source, without Telegram network/database stubs.
        # It checks the actual plugin manager against UIKit and actual model signatures.
        manager = source / 'submodules/SettingsUI/Sources/FullGramPluginManagerController.swift'
        if manager.exists():
            fullgram = source / 'submodules/TelegramCore/Sources/FullGram'
            models = [fullgram / name for name in (
                'FullGramIOSPluginEnvelope.swift', 'FullGramPythonRuntime.swift', 'FullGramNativeTextTools.swift', 'FullGramReactionTotalSettings.swift', 'FullGramGroupMentions.swift', 'FullGramPluginCatalog.swift', 'FullGramTextProgram.swift', 'FullGramPlugins.swift', 'FullGramAndroidPluginConverter.swift', 'FullGramCameraFlipPolicy.swift', 'FullGramChatColorSettings.swift', 'FullGramAdvancedSettings.swift', 'FullGramChatExportModels.swift', 'FullGramLocalNotificationSettings.swift', 'FullGramTranslationRequest.swift', 'FullGramGhostModeSettings.swift', 'FullGramDecoyState.swift', 'FullGramFeatureGate.swift', 'FullGramAppearanceSettings.swift',
                'FullGramMediaSendSettings.swift', 'FullGramInterfaceSettings.swift', 'FullGramGrantedGift.swift', 'FullGramMessageShotSettings.swift',
                'FullGramHiddenMessagesSettings.swift', 'FullGramReactionDisplaySettings.swift', 'FullGramRegexSettings.swift', 'FullGramHooks.swift')]
            with tempfile.TemporaryDirectory(prefix='fullgram-plugin-sdk-') as directory:
                flags = ['xcrun', 'swiftc', '-swift-version', '5', '-warnings-as-errors',
                         '-sdk', sdk, '-target', 'arm64-apple-ios15.0-simulator']
                result = subprocess.run([*flags, '-emit-module', '-module-name', 'TelegramCore',
                                         '-emit-module-path', str(Path(directory) / 'TelegramCore.swiftmodule'),
                                         *map(str, models)], capture_output=True, text=True)
                if result.returncode:
                    errors.append(f'Actual plugin model SDK harness:\n{result.stdout}{result.stderr}')
                else:
                    result = subprocess.run([*flags, '-emit-module', '-module-name', 'Display',
                                             '-emit-module-path', str(Path(directory) / 'Display.swiftmodule'),
                                             str(source / 'submodules/Display/Source/FullGramPluginAvatar.swift'),
                                             str(source / 'submodules/Display/Source/FullGramArcadeGameController.swift'),
                                             str(source / 'submodules/Display/Source/FullGramNativePlugins.swift')], capture_output=True, text=True)
                    if result.returncode:
                        errors.append(f'Actual plugin avatar SDK harness:\n{result.stdout}{result.stderr}')
                    else:
                        result = subprocess.run([*flags, '-typecheck', '-I', directory, str(manager),
                                                 str(source / 'submodules/SettingsUI/Sources/FullGramPluginPresentation.swift'),
                                                 str(source / 'submodules/SettingsUI/Sources/FullGramGroupMentionsController.swift'),
                                                 str(source / 'submodules/SettingsUI/Sources/FullGramPreferencesHubController.swift'),
                                                 str(source / 'submodules/TelegramUI/Components/VideoMessageCameraScreen/Sources/FullGramCameraFlipGestureRecognizer.swift')], capture_output=True, text=True)
                        if result.returncode:
                            errors.append(f'Actual plugin manager UIKit SDK check:\n{result.stdout}{result.stderr}')
                        else:
                            print('PASS: actual plugin manager checked against UIKit and actual model-only harness; full Telegram integration remains separate')
        # Compile just the actual artwork before starting the full Telegram target.
        icon_root = source / 'Telegram/Telegram-iOS'
        if (icon_root / 'FullGramOrange.icon').exists():
            icon_names = ['Telegram'] + sorted(path.stem for path in icon_root.glob('FullGram*.icon'))
            alternate_args = [argument for name in icon_names[1:] for argument in ('--alternate-app-icon', name)]
            with tempfile.TemporaryDirectory(prefix='fullgram-icon-sdk-') as directory:
                result = subprocess.run(['xcrun', 'actool', '--compile', directory,
                                         '--platform', 'iphoneos', '--minimum-deployment-target', '15.0',
                                         '--target-device', 'iphone', '--target-device', 'ipad',
                                         '--app-icon', 'Telegram', *alternate_args,
                                         '--output-partial-info-plist', str(Path(directory) / 'icons.plist'),
                                         *[str(icon_root / (name + '.icon')) for name in icon_names]],
                                        capture_output=True, text=True)
                if result.returncode:
                    errors.append(f'Icon Composer SDK compilation:\n{result.stdout}{result.stderr}')
                else:
                    compiled_icons = plistlib.loads((Path(directory) / 'icons.plist').read_bytes())
                    alternates = compiled_icons.get('CFBundleIcons', {}).get('CFBundleAlternateIcons', {})
                    if not set(icon_names[1:]).issubset(alternates):
                        errors.append('Icon Composer metadata is missing declared Full Gram alternate icons before the full build')
                    else:
                        print(f'PASS: {len(icon_names)} Icon Composer bundles and their metadata compiled before the full build')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(paths)} changed Swift sources parsed; UI import and Telegram API contracts checked. Full type checking still occurs during the native build.')


if __name__ == '__main__':
    main()
