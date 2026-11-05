// Tests of the 27.6 plugin APIs: the helpers that run in the plugin and the wrappers of host calls.
// PRELUDE points at FullGramScriptRuntime.swift or at a patch that adds it.
import assert from "node:assert/strict";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { loadPrelude, Sandbox } from "./mock.ts";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const prelude = loadPrelude(process.env.PRELUDE ?? path.join(root, "patches/fullgram-port-fixes.patch"));

function run(source: string, responders = {}) {
  const sandbox = new Sandbox({ prelude, responders });
  sandbox.load(`globalThis.out = (function () { ${source} })();`);
  const raw = (sandbox as any).context.out;
  // Values made in the sandbox have its own Array and Object; compare them as plain JSON.
  const out = raw && typeof raw.then === "function" ? raw.then((v: unknown) => JSON.parse(JSON.stringify(v))) : JSON.parse(JSON.stringify(raw));
  return { out, sandbox };
}

test("text helpers", () => {
  const { out } = run(`return [
    fullgram.text.capitalize('привет'), fullgram.text.titleCase('hello big world'), fullgram.text.reverse('a👍b'),
    fullgram.text.truncate('abcdefgh', 5), fullgram.text.slugify('Привет, Мир!'), fullgram.text.wordCount("it's a good-day, ok"),
    fullgram.text.charCount('👍🏽ab'), fullgram.text.stripEmoji('hi 👋 there'), fullgram.text.escapeHtml('<a href="x">'),
    fullgram.text.unescapeHtml('&lt;b&gt; &amp;'), fullgram.text.translit('Щука ёж'), fullgram.text.swapLayout('ghbdtn'),
    fullgram.text.mock('hello'), fullgram.text.between('a[b]c', '[', ']'), fullgram.text.template('Hi {name}, {x}', { name: 'Mei' })
  ];`);
  assert.deepEqual(out, ["Привет", "Hello Big World", "b👍a", "abcd…", "privet-mir", 4, 4, "hi there", "&lt;a href=&quot;x&quot;&gt;",
    "<b> &", "Shchuka yozh", "привет", "hElLo", "b", "Hi Mei, {x}"]);
});

test("date helpers", () => {
  const { out } = run(`
    const d = new Date(2026, 10, 3, 9, 5, 7);
    return [fullgram.date.format(d, 'DD.MM.YYYY HH:mm:ss'), fullgram.date.format(fullgram.date.addDays(d, 30), 'YYYY-MM-DD'),
      fullgram.date.diffDays(new Date(2026, 0, 1), new Date(2026, 0, 31)), fullgram.date.isToday(Date.now()),
      fullgram.date.startOfDay(d).getHours(), fullgram.date.parseDuration('1h 30m'), fullgram.date.parseDuration('nope'),
      fullgram.date.formatDuration(3723000, 'en'), fullgram.date.formatDuration(90000, 'ru'),
      fullgram.date.relative(Date.now() - 5 * 60000, 'ru'), fullgram.date.relative(Date.now() + 2 * 3600000, 'en'),
      fullgram.date.relative(Date.now() - 22 * 86400000, 'ru')];`);
  assert.deepEqual(out, ["03.11.2026 09:05:07", "2026-12-03", 30, true, 0, 5400000, null, "1h 2m 3s", "1 мин 30 с",
    "5 минут назад", "in 2 hours", "22 дня назад"]);
});

test("color, math and format helpers", () => {
  const { out } = run(`return [
    fullgram.color.hexToRgb('#0a0'), fullgram.color.rgbToHex(255, 128, 0), fullgram.color.lighten('#000000', 0.5), fullgram.color.darken('#FFFFFF', 0.25),
    fullgram.color.mix('#FF0000', '#0000FF'), fullgram.color.contrastText('#FFFF00'), /^#[0-9A-F]{6}$/.test(fullgram.color.random()),
    fullgram.math.clamp(15, 0, 10), fullgram.math.lerp(0, 10, 0.25), fullgram.math.round(3.14159, 2), fullgram.math.sum([1, 2, '3']),
    fullgram.math.average([2, 4]), fullgram.math.median([5, 1, 3, 2]), fullgram.math.percent(1, 4),
    (() => { const n = fullgram.math.randomInt(1, 3); return n >= 1 && n <= 3 && Number.isInteger(n); })(),
    (() => { const n = fullgram.math.random(5, 6); return n >= 5 && n < 6; })(),
    fullgram.format.bytes(1536), fullgram.format.bytes(512), fullgram.format.number(1234567.891), fullgram.format.plural(21, ['яблоко', 'яблока', 'яблок']),
    fullgram.format.plural(12, ['яблоко', 'яблока', 'яблок']), fullgram.format.plural(3, ['яблоко', 'яблока', 'яблок'])
  ];`);
  assert.deepEqual(out, [{ r: 0, g: 170, b: 0 }, "#FF8000", "#808080", "#BFBFBF", "#800080", "#000000", true, 10, 2.5, 3.14, 6, 3, 2.5, 25,
    true, true, "1.5 KB", "512 B", "1 234 567,89", "яблоко", "яблок", "яблока"]);
});

test("url, array, extract helpers", () => {
  const { out } = run(`return [
    fullgram.url.parse('https://Example.com:8080/a/b?x=1&y=hello%20world#top'), fullgram.url.build('https://a.b/c', { q: 'x y', n: 1, skip: null }),
    fullgram.url.param('https://a.b/?id=42', 'id'), fullgram.url.isUrl('https://t.me/x'), fullgram.url.isUrl('nope'),
    fullgram.url.extract('see https://a.b/c, and t.me/void.'), fullgram.url.domain('https://www.github.com/x'),
    fullgram.array.chunk([1, 2, 3, 4, 5], 2), fullgram.array.unique([1, 1, 2, 3, 3]), fullgram.array.unique([{ id: 1 }, { id: 1 }], 'id').length,
    fullgram.array.shuffle([1, 2, 3]).sort(), [1, 2].includes(fullgram.array.sample([1, 2])), fullgram.array.groupBy([1, 2, 3, 4], (n) => n % 2 ? 'odd' : 'even'),
    fullgram.array.sortBy([{ n: 2 }, { n: 1 }], 'n').map((x) => x.n), fullgram.array.sortBy([1, 3, 2], (x) => x, true),
    fullgram.extract.mentions('hi @Full Gram and @ab, mail a@b.com'), fullgram.extract.hashtags('#Привет и #ios_26'), fullgram.extract.emails('write me: me@void.gram!')
  ];`);
  assert.deepEqual(out, [
    { protocol: "https", host: "example.com", port: 8080, path: "/a/b", query: { x: "1", y: "hello world" }, hash: "top" },
    "https://a.b/c?q=x%20y&n=1", "42", true, false, ["https://a.b/c", "t.me/void"], "github.com",
    [[1, 2], [3, 4], [5]], [1, 2, 3], 1, [1, 2, 3], true, { odd: [1, 3], even: [2, 4] }, [1, 2], [3, 2, 1],
    ["@Full Gram"], ["#Привет", "#ios_26"], ["me@void.gram"]]);
});

test("host wrappers pass arguments and unwrap values", async () => {
  const { out, sandbox } = run(`return [
    fullgram.crypto.sha256('abc'), fullgram.crypto.uuid(), fullgram.encoding.base64Encode('hi'), fullgram.app.name(), fullgram.app.plugins(),
    fullgram.device.model(), fullgram.device.darkMode(), fullgram.speech.speak('привет', { rate: 0.5 }), fullgram.notify.schedule({ title: 't', seconds: 10 }),
    fullgram.haptics.pattern(['light', 'heavy'], 80)
  ];`, {
    "crypto.sha256": (a: any) => ({ value: "hash:" + a.text }), "crypto.uuid": () => ({ value: "u-1" }),
    "encoding.base64Encode": (a: any) => ({ value: Buffer.from(a.text).toString("base64") }), "app.name": () => ({ value: "Full Gram" }),
    "app.plugins": () => ({ value: [{ id: "x" }] }), "device.model": () => ({ value: "iPhone17,1" }), "device.darkMode": () => ({ value: true }),
    "notify.schedule": (a: any) => ({ value: "id-" + a.seconds })
  });
  assert.deepEqual(out, ["hash:abc", "u-1", "aGk=", "Full Gram", [{ id: "x" }], "iPhone17,1", true, true, "id-10", true]);
  const calls = sandbox.calls.map((c) => c.op);
  assert.ok(calls.includes("speech.speak") && calls.includes("haptics.pattern"));
  assert.deepEqual(sandbox.calls.find((c) => c.op === "haptics.pattern")!.args, { styles: ["light", "heavy"], interval: 80 });
  sandbox.dispose();
});

test("async helpers", async () => {
  const { out, sandbox } = run(`
    let tries = 0;
    return Promise.all([
      fullgram.async.sleep(5).then(() => 'slept'),
      fullgram.async.retry(() => { tries++; if (tries < 3) throw new Error('x'); return tries; }, 5, 1),
      fullgram.async.timeout(new Promise(() => {}), 10).catch((e) => e.message),
      fullgram.async.timeout(Promise.resolve(7), 50)
    ]);`);
  assert.deepEqual(await out, ["slept", 3, "Timed out after 10 ms", 7]);
  sandbox.dispose();
});

test("second batch: text, date, math, color", () => {
  const { out } = run(`
    const d = new Date(2026, 10, 7);
    return [
      fullgram.text.normalizeSpaces('  a   b \\n\\n\\n\\n c '), fullgram.text.removeUrls('see https://x.y/z now'), fullgram.text.removeMentions('hi @Full Gram !'),
      fullgram.text.detectScript('привет hi'), fullgram.text.detectScript('привет'), fullgram.text.wrap('one two three four', 9), fullgram.text.occurrences('abcabcab', 'ab'),
      fullgram.text.randomString(12).length, fullgram.text.randomString(1e15).length, fullgram.text.isEmojiOnly('👍 🔥'), fullgram.text.isEmojiOnly('hi 👍'), fullgram.text.firstLine('a\\nb'),
      fullgram.date.weekday(d, 'ru'), fullgram.date.monthName(d, 'en'), fullgram.date.isWeekend(d), fullgram.date.daysInMonth(new Date(2024, 1, 10)),
      fullgram.date.age(new Date(2012, 4, 8), new Date(2026, 10, 3)), fullgram.date.unix(new Date(1000000)), fullgram.date.fromUnix(1).getTime(),
      Object.keys(fullgram.date.countdown(Date.now() + 90061000)).join(','),
      fullgram.math.factorial(5), fullgram.math.gcd(12, 18), fullgram.math.lcm(4, 6), fullgram.math.isPrime(97), fullgram.math.isPrime(91), fullgram.math.isPrime(2), fullgram.math.fibonacci(10),
      fullgram.math.mod(-1, 5), fullgram.math.roundTo(17, 5), fullgram.math.range(5), fullgram.math.range(10, 0, -3),
      fullgram.color.toHsl('#FF0000'), fullgram.color.fromHsl(120, 100, 50), fullgram.color.invert('#000000'), fullgram.color.grayscale('#FF0000'), fullgram.color.rgba('#FF8000', 0.5)
    ];`);
  assert.deepEqual(out, ["a b\n\nc", "see now", "hi !", "mixed", "cyrillic", "one two\nthree\nfour", 3, 12, 10000, true, false, "a",
    "суббота", "November", true, 29, 14, 1000, 1000, "days,hours,minutes,seconds",
    120, 6, 12, true, false, true, 55, 4, 15, [0, 1, 2, 3, 4], [10, 7, 4, 1],
    { h: 0, s: 100, l: 50 }, "#00FF00", "#FFFFFF", "#363636", "rgba(255, 128, 0, 0.5)"]);
});

test("second batch: array, object, validate, storage", () => {
  const { out } = run(`return [
    fullgram.array.flatten([1, [2, [3]]]), fullgram.array.zip([1, 2, 3], ['a', 'b']), fullgram.array.countBy(['a', 'b', 'a']), fullgram.array.partition([1, 2, 3, 4], (n) => n > 2),
    fullgram.array.last([1, 2]), fullgram.array.compact([0, 1, null, '', 'x', false, NaN]), fullgram.array.intersect([1, 2, 3], [2, 3, 4]), fullgram.array.difference([1, 2, 3], [2]),
    fullgram.object.pick({ a: 1, b: 2 }, ['a']), fullgram.object.omit({ a: 1, b: 2 }, ['a']), fullgram.object.merge({ a: { x: 1 }, b: 1 }, { a: { y: 2 } }),
    fullgram.object.get({ a: { b: [5] } }, 'a.b.0'), fullgram.object.get({}, 'x.y', 'none'), fullgram.object.set({}, 'a.b', 3),
    fullgram.validate.email('me@void.gram'), fullgram.validate.email('nope@'), fullgram.validate.phone('+380 (67) 123-45-67'), fullgram.validate.username('@Full Gram'),
    fullgram.validate.username('ab'), fullgram.validate.hexColor('#abc'),
    (fullgram.storage.setJSON('cfg', { on: true }), fullgram.storage.getJSON('cfg')), fullgram.storage.has('cfg'), fullgram.storage.increment('n'), fullgram.storage.increment('n', 5),
    (fullgram.storage.remove('cfg'), fullgram.storage.has('cfg')), fullgram.storage.getJSON('missing', [])
  ];`);
  assert.deepEqual(out, [[1, 2, 3], [[1, "a"], [2, "b"]], { a: 2, b: 1 }, [[3, 4], [1, 2]], 2, [0, 1, "x"], [2, 3], [1, 3],
    { a: 1 }, { b: 2 }, { a: { x: 1, y: 2 }, b: 1 }, 5, "none", { a: { b: 3 } }, true, false, true, true, false, true,
    { on: true }, true, 1, 6, false, []]);
});
