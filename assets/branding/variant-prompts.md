# App-icon variant generation

Method: built-in image generation. Edit target:
`Telegram/Telegram-iOS/Telegram.icon/Assets/FullGram.png` from the owner's artwork.
Generated images were inspected and copied into project assets without replacing
the white original. The generated files retain the reference's 1254-pixel square
canvas; Icon Composer compiles the platform-specific outputs.

Full Gram ships exactly four icons: White (primary), Orange, Red and runa.

## White

The owner's default artwork: a silver/white emblem on a dark faceted background.
It stays as the primary `Telegram.icon` bundle.

## Orange

Edit this app-icon artwork into a rich orange / amber color variant. Preserve
the exact central emblem silhouette with the inset paper-airplane geometry and
its size and placement. Only recolor the purple background radial faceted rays
and the small lavender plane accent to orange. Flat full-bleed square 1024x1024
image, opaque, sharp clean edges. No rounded-corner mask, no outside margin, no
text, no border, no mockup, no added objects. This will be used directly as an
iOS app icon.

## Red

Edit this app-icon artwork into a red / crimson color variant. Preserve the exact
central emblem silhouette with the inset paper-airplane geometry and its size and
placement. Only recolor the purple background radial faceted rays and the small
lavender plane accent to red. Flat full-bleed square 1024x1024 image, opaque,
sharp clean edges. No rounded-corner mask, no outside margin, no text, no border,
no mockup, no added objects. This will be used directly as an iOS app icon.

## runa

The owner-provided runa (mascot) illustration is used as-is at full bleed. It is not
recolored or regenerated; `assets/branding/fullgram/classic/MeiMei.png` is the
source artwork copied into the `FullGramMascot` bundle.
