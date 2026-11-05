#!/usr/bin/env python3
"""Apply the native port patches only to their pinned upstream source tree."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
from port_sources import missing_port_sources

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent
source = args.source.resolve()
pin = json.loads((root / "upstream.json").read_text())
actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
if actual != pin["commit"]:
    raise SystemExit("Upstream commit differs from upstream.json; refusing to apply a mismatched patch")
patches = [
    root / "patches" / "fullgram-ghost-mode.patch",
    root / "patches" / "fullgram-custom-features.patch",
    root / "patches" / "fullgram-followup-features.patch",
    root / "patches" / "fullgram-interface-controls.patch",
    root / "patches" / "fullgram-haptics-material.patch",
    root / "patches" / "fullgram-attachment-menu-motion.patch",
    root / "patches" / "fullgram-lyrics-word-sync.patch",
    root / "patches" / "fullgram-formatting-toolbar-layout.patch",
    root / "patches" / "fullgram-plugin-dialogs-keyboard.patch",
    root / "patches" / "fullgram-music-reference.patch",
    root / "patches" / "fullgram-peer-search.patch",
    root / "patches" / "fullgram-player-toolbar-refinements.patch",
    root / "patches" / "fullgram-music-inline-queue.patch",
    root / "patches" / "fullgram-fixed-player-fades.patch",
    root / "patches" / "fullgram-expanded-lyrics.patch",
    root / "patches" / "fullgram-big-update.patch",
    root / "patches" / "fullgram-settings-optimization.patch",
    root / "patches" / "fullgram-port-fixes.patch",
    root / "patches" / "fullgram-blur-glass-corners.patch",
    root / "patches" / "fullgram-feature-gate.patch",
]
for patch in patches:
    subprocess.run(["git", "apply", "--recount", "--check", str(patch)], cwd=source, check=True)
    subprocess.run(["git", "apply", "--recount", str(patch)], cwd=source, check=True)

# Full Gram ships exactly four launcher icons: white (the primary Telegram icon),
# orange, red and the mascot. The patches still carry the historical bundle
# names, so rename them here: iOS caches an alternate icon by name, and fresh names
# also guarantee that the new artwork is rendered by SpringBoard.
fullgram = root / "assets/branding/fullgram"
icons = source / "Telegram/Telegram-iOS"
image_assets = source / "submodules/TelegramUI/Images.xcassets/FullGram"


def clear_directory(path: Path) -> None:
    for child in path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

for old, new in (("FullGramBlue", "FullGramOrange"), ("FullGramGraphite", "FullGramRed"), ("FullGramOriginalChibi", "FullGramMascot")):
    old_bundle = icons / (old + ".icon")
    new_bundle = icons / (new + ".icon")
    if new_bundle.exists():
        shutil.rmtree(new_bundle)
    if not old_bundle.is_dir():
        raise SystemExit(f"Port patch is missing the {old}.icon bundle")
    old_bundle.rename(new_bundle)

keep_bundles = {"FullGramOrange.icon", "FullGramRed.icon", "FullGramMascot.icon"}
for bundle in icons.glob("Full Gram*.icon"):
    if bundle.name not in keep_bundles:
        shutil.rmtree(bundle)

# One full-bleed layer per icon. The source artwork keeps its historical file
# names (Brand = white, Blue = orange, Graphite = red, Mascot = mascot).
launcher_icons = {
    "Telegram": fullgram / "Brand.png",
    "FullGramOrange": fullgram / "Blue.png",
    "FullGramRed": fullgram / "Graphite.png",
    "FullGramMascot": fullgram / "classic" / "MeiMei.png",
}
for folder, artwork in launcher_icons.items():
    bundle = icons / (folder + ".icon")
    assets = bundle / "Assets"
    clear_directory(assets)
    shutil.copy2(artwork, assets / "FullGram.png")
    icon = json.loads((bundle / "icon.json").read_text())
    for group in icon["groups"]:
        for layer in group["layers"]:
            layer["image-name"] = "FullGram.png"
            layer.pop("position", None)
    (bundle / "icon.json").write_text(json.dumps(icon, indent=2) + "\n")

# Drop the extra icon bundles and their picker previews. OriginalFullGram2 stays for
# the settings logo; the other imagesets are used by the four picker entries.
for name in (
    "GlassBlue", "GlassGraphite", "OriginalDefault", "OriginalAlt", "OriginalBard",
    "OriginalChibi2", "OriginalDiscord", "OriginalFullGram", "OriginalNothing",
    "OriginalSpotify", "OriginalWin95", "OriginalYaplus",
):
    image_set = image_assets / (name + ".imageset")
    if image_set.is_dir():
        shutil.rmtree(image_set)

# The largest in-app logo is 100 pt (FullGramSettingsHeaderItem); the icon picker is
# at most 72 pt. Ship 300 px previews for 3x screens instead of decoding 1254 px
# launcher artwork in these rows. Icon Composer keeps its full-size originals.
picker_previews = {
    "Brand": root / "assets/branding/previews" / "Brand.png",
    "Blue": root / "assets/branding/previews" / "Blue.png",
    "Graphite": root / "assets/branding/previews" / "Graphite.png",
    "OriginalChibi": fullgram / "classic" / "MeiMei-Preview.png",
}
for name, preview in picker_previews.items():
    image_set = image_assets / (name + ".imageset")
    clear_directory(image_set)
    shutil.copy2(preview, image_set / "FullGram.png")
    contents = {"images": [{"idiom": "universal", "filename": "FullGram.png", "scale": "3x"}], "info": {"author": "xcode", "version": 1}}
    (image_set / "Contents.json").write_text(json.dumps(contents, indent=2) + "\n")

# TelegramUIResources includes Resources/**/* in the application bundle.
font_src = root / "assets" / "fonts" / "YSMusic-HeadlineBold.ttf"
font_dst = source / "submodules" / "TelegramUI" / "Resources" / font_src.name
font_dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(font_src, font_dst)

# Full Gram settings pull-down easter egg image, bundled the same way.
eblan_src = root / "assets" / "easter" / "FullGramEblan.png"
if eblan_src.is_file():
    shutil.copy2(eblan_src, source / "submodules" / "TelegramUI" / "Resources" / eblan_src.name)

missing = missing_port_sources(source)
if missing:
    raise SystemExit("Port patch is missing required native source files:\n" + "\n".join(missing))
print("Applied native Full Gram changes to " + actual)
