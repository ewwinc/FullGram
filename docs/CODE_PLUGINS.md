# Code plugins (JavaScript, Lua, Python, Rust)

Code plugins are JavaScript, Lua, Python or Rust (WebAssembly) files that run as code inside the
app and change how it behaves.
They sit beside the existing declarative `.plugin` / `.iosplug` (JSON) plugins, which keep
working unchanged.

## Isolation

iOS does not let an app start processes or load downloaded native code, so each plugin gets
its own **JavaScriptCore virtual machine on its own serial queue**:

- an exception stays inside the plugin and is reported to the plugin console;
- a hook that does not answer within **250 ms** (2 s with *Developer → Relaxed plugin limits*)
  disables the plugin, removes all of its hooks and shows a notice, so a stuck plugin can never
  freeze the app again;
- plugins have **no network, account, file or message-sending API**. They only see the text
  passed to their hooks and their own 64 KB key-value storage.

Python plugins run in [PocketPy](https://github.com/pocketpy/pocketpy) 2.1.8, built without its
`os`/`io` layer (no files, sockets, `system()` or `dlopen`) and with a watchdog that stops a
call running past its time limit. Rust plugins are WebAssembly modules run by WAMR's interpreter
(no JIT); their only import is `fullgram.host`. Both engines live in `submodules/FullGramPluginEngines` of
the port (see `patches/fullgram-big-update.patch`).

## Install

- Plugins screen → **+** → pick a `.js`, `.fullgramjs`, `.py`, `.fullgrampy` or `.wasm` file, or
- tap a `.fullgramjs` / `.fullgram.js` file in a chat.

The confirmation shows the plugin's header and what it may do. The list shows the name, version
and language; toggle, restart (tap) and delete (swipe) a row.

## Header

```js
// ==FullGramPlugin==
// @id my-plugin            (a–z, 0–9, - and _; defaults to the file name)
// @name My plugin
// @author Me
// @version 1.0
// @description What it does.
// ==/FullGramPlugin==
```

## API

| Call | Effect |
| --- | --- |
| `fullgram.hooks.before(point, fn)` | runs `fn(text, ctx)` before the native handler |
| `fullgram.hooks.replace(point, fn)` | **replaces** the native handler; only one plugin may replace a point (later ones become `after`) |
| `fullgram.hooks.after(point, fn)` | runs after the native handler |
| `fullgram.features.disable(name)` / `enable(name)` | switches a native feature off/on while the plugin runs |
| `fullgram.on(event, fn)` | `load`, `unload`, `chatOpen` (`{ peerId }`) |
| `fullgram.storage.get(key)` / `set(key, value)` | per-plugin strings, 64 KB total |
| `fullgram.toast(text)`, `fullgram.log/warn/error(...)`, `console.*`, `print` | messages and console output |
| `setTimeout`, `setInterval` (≥ 100 ms), `clearTimeout` | timers on the plugin queue |

A text hook returns the new text, or anything that is not a string to leave it unchanged.
`ctx` is `{ peerId, isSecret }`.

### Hook points

| Point | Native handler |
| --- | --- |
| `message.outgoing.text` (`fullgram.hooks.points.outgoingText`) | JSON plugins' outgoing replacements; applies to plain cloud-chat text without entities or media, never secret chats |

### Features

`fastShare`, `messageShot`, `reactionPicker`, `readSummary`, `editedInfo`, `messageDetails`,
`stories`, `similarChannels`, `premiumStatuses`, `unreadCounters`, `greetingSticker`,
`openLinkWarning`, `doubleTapToEdit`, `formattingToolbar`, `keyboardHideOnScroll`.

Each maps onto the matching Full Gram interface setting, so every place that honours the setting
honours the plugin. Overrides are never written to the user's settings and vanish when the
plugin stops.

### WhiteGram compatibility

`wg.registerPlugin`, `wg.BasePlugin`, `wg.on`, `wg.log`, `wg.toast`, `wg.getStorage` and
`wg.setStorage` map onto the API above. UI-building calls of the old WhiteGram runtime are not
provided.

### Injecting plugins (inject API)

These calls change the app itself, so they work only for **trusted** plugins (see *Safe zone*):

| Call | Effect |
| --- | --- |
| `fullgram.player.state()` | `{ title, artist, duration, position, playing }` of the music player |
| `fullgram.player.control(action)`, `play()`, `pause()`, `next()`, `previous()` | `play`, `pause`, `toggle`, `next`, `previous` |
| `fullgram.on('trackChange', fn)` | `{ title, artist, duration }` when a new track starts |
| `fullgram.hooks.before('lyrics.text', fn)` | song lyrics before they are shown, one line per `\n`; return the same number of lines (an empty line drops it, timings stay) |

A plugin declares that it injects with `// @inject true` (`# @inject true` in Python,
`"inject": true` in a Rust manifest).

### Plugin settings

`fullgram.settings.declare([{ key, type: 'toggle' | 'text', title, subtitle, default }])` makes the app
draw the plugin's own settings (tap the plugin in the list; lyrics plugins also appear under
*Lyrics sources*). `fullgram.settings.get(key)` reads a value (`"1"`/`"0"` for switches); the
`settingsChange` event reports changes.

### Interface API

Every call is declarative: the plugin describes, Full Gram draws, and everything a plugin created
disappears when it stops. Each group needs a permission in the header, e.g.
`// @permissions ui, menu, overlay` (`# @permissions …` in Python, `"permissions": ["ui"]` in a
Rust manifest). The install confirmation lists them; a call without its permission fails with a
console error.

| Call | Permission | Effect |
| --- | --- | --- |
| `fullgram.ui.alert({ title, message, buttons: [{ id, title, style }] }, fn)` | `ui` | alert; `fn(buttonId)` |
| `fullgram.ui.sheet({ title, message, items: [{ id, title }] }, fn)` | `ui` | action sheet; `fn(itemId or null)` |
| `fullgram.ui.menu.add({ id, title, icon, media })` / `remove(id)` | `menu` | item in the message menu (5 per plugin, SF Symbol `icon`; `media: 'photo'` shows it only on messages with a photo); taps send `menuAction` `{ itemId, messageId, peerId, text }` |
| `fullgram.ui.profile.addBlock({ peerId?, block: { id, title, text } })` / `removeBlock(id)` | `profile` | text block in user profiles (all, or one `peerId`) |
| `fullgram.ui.profile.addButton({ peerId?, button: { id, title } })` / `removeButton(id)` | `profile` | button in profiles; taps send `profileButton` `{ buttonId, peerId }` |
| `fullgram.ui.overlay.create({ id, effect, amount, speed, color })` / `update(id, …)` / `remove(id)` | `overlay` | particles over the whole app: `snow`, `leaves`, `rain`, `stars`, `confetti`; `amount`/`speed` 0.1–3; never takes touches, paused by Reduce Motion |
| `fullgram.ui.overlay.addText({ id, text, anchor, size, color })` | `overlay` | text pinned to `topLeft`, `topRight`, `bottomLeft`, `bottomRight` or `center` |
| `fullgram.ui.font.set({ element, size })` / `reset(element)` | `fonts` | `messages` or `lists` text size in points (12–30), applied when the appearance is rebuilt |
| `fullgram.ui.badge.add({ peerId, badge: { text } })` / `remove({ peerId })` | `badges` | badge beside a chat's name in the chat list |
| `fullgram.media.cutOutSticker(peerId, messageId)` → Promise | `messages` | lifts the subject off the message's photo and sends it as a sticker to the open chat (iOS 17) |
| `fullgram.media.describePhoto(peerId, messageId)` → Promise<string or null> | `messages.read` | on-device description and text of the message's photo |
| `fullgram.tools.chatStats(peerId)` → Promise | `messages.read` | the app's chat statistics sheet for every message stored on the device |
| `fullgram.tools.yearInReview(peerId)` → Promise | `messages.read` | the app's year-in-review sheet for the chat |
| `fullgram.tools.downloadChatMedia(peerId)` → Promise | `messages.read` | saves the chat's photos, videos and files (up to 500) into one folder |
| `fullgram.messages.stats({ peerId })` → Promise<ChatStats> | `messages.read` | counts, round-video and voice counts, frequent and rare words, first/last message dates over the chat's stored messages |
| `fullgram.ui.gifts.catalog.list(fn)` → Promise | — | Telegram's gift catalog, read-only: `[{ giftId, title, stars, fileId, limited, remains, total, soldOut }]` (Python: `fullgram.ui.gifts.catalog.list(fn)`) |
| `fullgram.clipboard.write(text)` | `clipboard` | copy text |
| `fullgram.device.info()` | `device` | `{ battery, charging, orientation, lowPowerMode, reduceMotion, locale }` |
| `fullgram.haptics.play(style)` | `haptics` | `light`, `medium`, `heavy`, `soft`, `rigid`, `selection`, `success`, `warning`, `error` (off with “No vibration”) |

`peerId` is the value plugins receive in events and hook contexts. Python has the same names
(`fullgram.ui.menu.add({...})`, `fullgram.call('device.info')`); Rust has `fullgram_plugin::call(op, json)`
and helpers in `fullgram_plugin::ui`.

`ChatStats` is `{ count, voices, roundVideos, firstDate, lastDate, frequentWords, rareWords,
wordSampleSize, truncated }`. Dates are Unix seconds (`null` for an empty chat), word lists are
`[{ word, count }]`, and `wordSampleSize` shows how many newest messages the word counts cover.

The bundled example is `code-plugins/chat-info/plugin.fullgram.js`: long-press any message →
«Инфа о чате».

### Utility API (27.6)

One hundred and fifty-two calls added in 27.6. Types are in `sdk/typescript/fullgram.d.ts`; tests are in
`tools/mock-runner/api276.test.ts` (`PRELUDE=…/FullGramScriptRuntime.swift node --test api276.test.ts`).

Answered by the app:

- `fullgram.crypto`: `sha256`, `sha1`, `sha512`, `md5`, `hmac(key, text)` (hex), `randomBytes(n)` (base64), `uuid()`. No permission.
- `fullgram.encoding`: `base64Encode`, `base64Decode`, `hexEncode`, `hexDecode`. No permission.
- `fullgram.app`: `version()`, `build()`, `name()`, `plugins()`. No permission.
- `fullgram.device` (`device`): `battery()`, `isCharging()`, `screen()`, `darkMode()`, `model()`, `systemVersion()`, `timezone()`, `isLowPower()`, `freeDisk()`, `memory()`, `uptime()`, `thermalState()`. Battery, charging, screen and dark mode come from a snapshot the main thread refreshes after each read, so the first read can return the defaults.
- `fullgram.clipboard`: `read()` (`clipboard.read`, a Promise; iOS shows its paste notice), `hasText()` (Promise), `clear()` (`clipboard`).
- `fullgram.speech` (`ui`): `speak(text, { language, rate })`, `stop()`, `isSpeaking()`, `voices()`.
- `fullgram.notify` (`notifications`): `schedule({ id, title, body, seconds })` returns the id; `cancel(id)`, `cancelAll()`. A plugin sees only its own reminders.
- `fullgram.haptics.pattern(styles, interval)`: up to 16 taps (`haptics`).

Run inside the plugin, no permission:

- `fullgram.text`: `capitalize`, `titleCase`, `reverse`, `truncate`, `slugify`, `wordCount`, `charCount`, `stripEmoji`, `escapeHtml`, `unescapeHtml`, `translit`, `swapLayout` (ghbdtn ⇄ привет), `mock`, `between`, `template`.
- `fullgram.date`: `format(date, 'DD.MM.YYYY HH:mm')`, `relative`, `addDays`, `diffDays`, `isToday`, `startOfDay`, `parseDuration('1h 30m')`, `formatDuration`.
- `fullgram.color`: `hexToRgb`, `rgbToHex`, `lighten`, `darken`, `mix`, `contrastText`, `random`.
- `fullgram.math`: `clamp`, `lerp`, `random`, `randomInt`, `round`, `sum`, `average`, `median`, `percent`.
- `fullgram.url`: `parse`, `build`, `param`, `isUrl`, `extract`, `domain`.
- `fullgram.array`: `chunk`, `unique`, `shuffle`, `sample`, `groupBy`, `sortBy`.
- `fullgram.async`: `sleep`, `debounce`, `throttle`, `retry`, `timeout`.
- `fullgram.format`: `bytes`, `number`, `plural(n, ['яблоко', 'яблока', 'яблок'])`.
- `fullgram.extract`: `mentions`, `hashtags`, `emails`.

The second batch (52 more, also in the prelude, no permission):

- `fullgram.text`: `normalizeSpaces`, `removeUrls`, `removeMentions`, `detectScript`, `wrap(text, width)`, `occurrences`, `randomString` (up to 10000), `isEmojiOnly`, `firstLine`.
- `fullgram.date`: `weekday`, `monthName`, `isWeekend`, `daysInMonth`, `age`, `unix`, `fromUnix`, `countdown`.
- `fullgram.math`: `factorial`, `gcd`, `lcm`, `isPrime` (null above 10¹²), `fibonacci`, `mod`, `roundTo`, `range` (up to 100000 numbers).
- `fullgram.color`: `toHsl`, `fromHsl`, `invert`, `grayscale`, `rgba`.
- `fullgram.array`: `flatten`, `zip`, `countBy`, `partition`, `last`, `compact` (keeps 0), `intersect`, `difference`.
- `fullgram.object`: `pick`, `omit`, `merge` (deep), `get('a.b.0')`, `set('a.b', value)`.
- `fullgram.validate`: `email`, `phone`, `username`, `hexColor`.
- `fullgram.storage`: `remove`, `has`, `getJSON`, `setJSON`, `increment`.

### Events

`load`, `unload`, `chatOpen`, `chatClose`, `profileOpen`, `profileClose`, `screenChange`,
`appForeground`, `appBackground`, `accountChange` (`{ accountId }`), `settingsChange`, `menuAction`,
`profileButton`, `uiResult` and, for injecting plugins, `trackChange`.

### Setting types

`fullgram.settings.declare` accepts `toggle`, `text`, `slider` (`min`, `max`, `step`), `color`
(`#RRGGBB`), `select` (`options: [{ value, title }]`) and `preview` (read-only text).

## Safe zone

- Ordinary plugins (outgoing text, switching features off, storage, toasts, settings) install
  from anywhere.
- Manual installs are treated as unofficial: an injecting plugin needs *Developer → Injecting
  plugins from unofficial sources* and a disclaimer that the responsibility is entirely the user's.
- The inject API is also checked while the plugin runs: an untrusted plugin calling it gets an
  error in the console.

## Python plugins

One file with the same header in `#` comments; the `fullgram` object is already defined and accepts
decorators:

```python
# ==FullGramPlugin==
# @id shout
# @name Shout
# @author Me
# @version 1.0
# ==/FullGramPlugin==

@fullgram.hooks.before(fullgram.hooks.points.outgoing_text)
def shout(text, ctx):
    return text + '!'
```

PocketPy is a Python 3 subset: no file imports, and `str.lower()`/`upper()` only fold Latin
letters. Example: [`examples/python/lyrics-cleaner.fullgram.py`](examples/python/lyrics-cleaner.fullgram.py).

## Rust plugins

Use the dependency-free SDK in [`sdk/rust`](../sdk/rust) and build a `cdylib`:

```sh
cd docs/examples/rust/emoji-shortcuts
cargo build --release --target wasm32-unknown-unknown
# target/wasm32-unknown-unknown/release/emoji_shortcuts_rs.wasm is the plugin
```

```rust
use fullgram_plugin::{hooks, manifest};

manifest!(br#"{"id":"shout-rs","name":"Shout","author":"Me","version":"1.0"}"#);

#[no_mangle]
pub extern "C" fn fullgram_init() {
    hooks::before(hooks::OUTGOING_TEXT, |text, _ctx| Some(format!("{}!", text)));
}
```

The manifest is the `fullgram.manifest` custom section the app reads before running anything. The
module exports `fullgram_alloc`, `fullgram_free` and `fullgram_dispatch` (from the SDK) and imports only
`fullgram.host`; every message is JSON. Example:
[`examples/rust/emoji-shortcuts`](examples/rust/emoji-shortcuts).

## Debugging

*Settings → Full Gram → Developer*: **Plugin console** shows `print`, errors and hook activity;
**Relaxed plugin limits** lengthens the hook timeout and turns script errors into toasts;
**Verbose logging** writes them to a shareable log file.

Example: [`examples/smart-quotes.fullgram.js`](examples/smart-quotes.fullgram.js).
Prelude tests: `node runtime/tests/fullgramscript/test_prelude.js /path/to/prepared/telegram`.
