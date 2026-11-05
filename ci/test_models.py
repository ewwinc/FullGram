"""Run the actual Full Gram models through the pinned Postbox codec before the app build.

Only the standalone codec, its native support files and MurMurHash32 are compiled. No database, SDK stubs,
copied encoder implementations or TelegramCore module build is involved.
"""
import argparse
from pathlib import Path
import platform
import subprocess
import tempfile
from test_local_policies import run as run_local_policies


def run(source: Path):
    if platform.system() != 'Darwin':
        raise SystemExit('The actual Postbox host tests require the macOS build machine.')
    source = source.resolve()
    run_local_policies(source)
    with tempfile.TemporaryDirectory(prefix='fullgram-postbox-tests-') as directory:
        output = Path(directory)
        subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-warnings-as-errors',
                        str(source / 'submodules/TelegramUI/Sources/FullGramStartupStorage.swift'),
                        str(source / 'tools/fullgram-tests/startup/main.swift'),
                        '-o', str(output / 'startup-tests')], check=True)
        subprocess.run([str(output / 'startup-tests')], check=True)
        subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-warnings-as-errors',
                        str(source / 'submodules/TelegramUI/Sources/FullGramMusicHapticsTimeline.swift'),
                        str(source / 'tools/fullgram-tests/music-haptics/main.swift'),
                        '-o', str(output / 'music-haptics-tests')], check=True)
        subprocess.run([str(output / 'music-haptics-tests')], check=True)
        subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-warnings-as-errors',
                        str(source / 'submodules/TelegramCore/Sources/FullGram/FullGramHistoryTextDiff.swift'),
                        str(source / 'submodules/Display/Source/FullGramPlayerTextStyle.swift'),
                        str(source / 'tools/fullgram-tests/daily-ux/main.swift'),
                        '-o', str(output / 'daily-ux-tests')], check=True)
        subprocess.run([str(output / 'daily-ux-tests')], check=True)
        subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-warnings-as-errors',
                        str(source / 'submodules/Display/Source/FullGramNativePlugins.swift'),
                        str(source / 'tools/fullgram-tests/iosplug-native/main.swift'),
                        '-o', str(output / 'native-iosplug-tests')], check=True)
        subprocess.run([str(output / 'native-iosplug-tests'),
                        str(Path(__file__).resolve().parents[1] / 'plug')], check=True)
        subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-warnings-as-errors',
                        str(source / 'submodules/TelegramUI/Sources/FullGramMusicMetadata.swift'),
                        str(source / 'submodules/TelegramUI/Sources/FullGramLyricsLookup.swift'),
                        str(source / 'submodules/TelegramUI/Sources/FullGramLyricsProviders.swift'),
                        str(source / 'submodules/TelegramUI/Sources/FullGramLyricsAligner.swift'),
                        str(source / 'submodules/TelegramUI/Sources/FullGramLyricsTiming.swift'),
                        str(source / 'submodules/TelegramUI/Sources/FullGramLyricsYaml.swift'),
                        str(source / 'tools/fullgram-tests/lyrics/main.swift'),
                        '-o', str(output / 'lyrics-tests')], check=True)
        subprocess.run([str(output / 'lyrics-tests')], check=True)
        murmur = source / 'submodules/MurMurHash32'
        header = murmur / 'PublicHeaders/MurMurHash32/MurMurHash32.h'
        (output / 'module.modulemap').write_text(
            'module MurMurHash32 { header "' + str(header) + '" export * }\n', encoding='utf-8')
        subprocess.run(['xcrun', 'clang', '-fmodules', '-fobjc-arc',
                        '-I', str(murmur / 'PublicHeaders'), '-c',
                        str(murmur / 'Sources/MurMurHash32.m'), '-o', str(output / 'murmur.o')], check=True)
        postbox = source / 'submodules/Postbox/Sources'
        # Coding.swift uses the comparator in ValueBoxKey and the shared logger.
        # Compile their actual upstream implementations in the same module.
        codec = [postbox / 'Coding.swift', postbox / 'ValueBoxKey.swift', postbox / 'PostboxLogging.swift',
                 *sorted((postbox / 'Utils/Encoder').glob('*.swift')),
                 *sorted((postbox / 'Utils/Decoder').glob('*.swift'))]
        subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-emit-library', '-emit-module',
                        '-module-name', 'Postbox', '-I', str(output),
                        '-emit-module-path', str(output / 'Postbox.swiftmodule'),
                        *map(str, codec), str(output / 'murmur.o'),
                        '-o', str(output / 'libPostbox.dylib')], check=True)
        fullgram = source / 'submodules/TelegramCore/Sources/FullGram'
        models = [fullgram / name for name in ('FullGramIOSPluginEnvelope.swift', 'FullGramNativeTextTools.swift', 'FullGramReactionTotalSettings.swift', 'FullGramGroupMentions.swift', 'FullGramPluginCatalog.swift', 'FullGramTextProgram.swift', 'FullGramPlugins.swift', 'FullGramAndroidPluginConverter.swift', 'FullGramCameraFlipPolicy.swift', 'FullGramChatColorSettings.swift', 'FullGramAdvancedSettings.swift', 'FullGramChatExportModels.swift', 'FullGramLocalNotificationSettings.swift', 'FullGramTranslationRequest.swift', 'FullGramGhostModeSettings.swift', 'FullGramDecoyState.swift', 'FullGramFeatureGate.swift', 'FullGramAppearanceSettings.swift', 'FullGramMediaSendSettings.swift', 'FullGramInterfaceSettings.swift', 'FullGramGrantedGift.swift', 'FullGramMessageShotPolicy.swift', 'FullGramMessageShotSettings.swift', 'FullGramHiddenMessagesSettings.swift', 'FullGramReactionDisplaySettings.swift', 'FullGramTextToolsPolicy.swift', 'FullGramRegexSettings.swift',
                                         'FullGramArchiveFileStore.swift', 'FullGramMessageHistoryState.swift', 'FullGramHooks.swift')]
        subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-warnings-as-errors',
                        '-D', 'FULLGRAM_POSTBOX_TESTS', '-I', str(output), '-L', str(output), '-lPostbox',
                        '-Xlinker', '-rpath', '-Xlinker', str(output),
                        *map(str, models), str(source / 'tools/fullgram-tests/main.swift'),
                        '-o', str(output / 'fullgram-tests')], check=True)
        subprocess.run([str(output / 'fullgram-tests'), str(Path(__file__).resolve().parents[1] / 'plugins')], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    run(parser.parse_args().source)
