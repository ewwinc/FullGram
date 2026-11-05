# App icon presets

Full Gram ships exactly four launcher icons:

1. White — the primary `Telegram.icon` bundle (`FullGram/Brand` preview).
2. Orange — the `FullGramOrange` alternate bundle (`FullGram/Blue` preview).
3. Red — the `FullGramRed` alternate bundle (`FullGram/Graphite` preview).
4. Mascot — the `FullGramMascot` alternate bundle (`FullGram/OriginalChibi` preview, Mascot artwork).

The owner-provided artwork lives in
[source-artwork](source-artwork): `Default.jpg` (white), `Orange.jpg`, `Red.jpg`
and `Mascot.jpg`. The prepared full-bleed PNGs are `fullgram/Brand.png`,
`fullgram/Blue.png`, `fullgram/Graphite.png` and `fullgram/classic/MeiMei.png`.

`FullGramAppIconCatalog` exposes the same four choices to SettingsUI and the
application icon bindings. `ci/prepare.py` renames the historical patch bundle
names to `FullGramOrange`, `FullGramRed` and `FullGramMascot`, copies the artwork, and removes
the unused icon bundles and previews.
