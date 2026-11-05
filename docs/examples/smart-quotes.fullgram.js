// ==FullGramPlugin==
// @id smart-quotes
// @name Smart quotes
// @author FullGram-IOS
// @version 1.0
// @description Replaces the outgoing-text handler: straight quotes become «ёлочки» or “curly” quotes, "--" becomes an em dash. Turns off the fast-share button as a feature-toggle example.
// ==/FullGramPlugin==

const style = fullgram.storage.get('style') || 'auto';

function curly(text, ctx) {
    const russian = style === 'ru' || (style === 'auto' && /[а-яё]/i.test(text));
    let open = true;
    return text
        .replace(/--/g, '—')
        .replace(/"/g, () => {
            const mark = russian ? (open ? '«' : '»') : (open ? '“' : '”');
            open = !open;
            return mark;
        });
}

// `replace` disables the native outgoing-text handler (JSON .plugin outgoing rules) while
// this plugin is on; use `before`/`after` to run alongside it instead.
fullgram.hooks.replace(fullgram.hooks.points.outgoingText, curly);

fullgram.features.disable('fastShare');

fullgram.on('chatOpen', ({ peerId }) => fullgram.log('chat opened', peerId));
fullgram.on('unload', () => fullgram.log('smart quotes off'));
fullgram.log('smart quotes ready, style =', style);
