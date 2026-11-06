"""The Full Gram app icons, from mark.py. Run from this folder (needs rsvg-convert and Pillow):
Brand (white), Blue (orange) and Graphite (red) at 1254 px plus 300 px in-app previews.
The mascot artwork is the owner-provided PNG in classic/MeiMei.png."""
import subprocess
from PIL import Image
import mark

def render(svg, path):
    open("icon.svg", "w").write(svg)
    subprocess.run(["rsvg-convert", "icon.svg", "-o", path], check=True)

def flatten(path):
    Image.open(path).convert("RGB").save(path, optimize=True)

FULL = {
    "Brand": (("#3B3B3B", "#070707"), "#FFFFFF", "#BBBBBB"),
    "Blue": (("#2B4C9B", "#0A1636"), "#FFFFFF", "#A9BCEB"),
    "Graphite": (("#F4F4F4", "#C7C7C7"), "#121212", "#6F6F6F"),
}
for name, (background, blade, core) in FULL.items():
    render(mark.svg(1254, background, blade, core), name + ".png")
    flatten(name + ".png")
    Image.open(name + ".png").resize((300, 300), Image.LANCZOS).save("../previews/%s.png" % name, optimize=True)

render(mark.svg(1254, None, scale=0.8), "FullGram-mark.png")
open("FullGram-mark.svg", "w").write(mark.svg(1024, None, scale=0.8))
open("FullGram-icon.svg", "w").write(mark.svg(1024, ("#3B3B3B", "#070707")))
