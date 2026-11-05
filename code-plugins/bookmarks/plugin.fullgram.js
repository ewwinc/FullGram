// ==FullGramPlugin==
// @id bookmarks
// @name Закладки
// @author Full Gram
// @version 1.0.0
// @description Пункт «В закладки» в меню сообщения. Закладки с тегами открываются в Настройки → Full Gram → Инструменты → Закладки.
// @permissions menu, ui, messages
// ==/FullGramPlugin==

(function () {
    'use strict';
    fullgram.settings.declare([
        { key: 'tag', type: 'text', title: 'Тег по умолчанию', subtitle: 'Например «прочитать позже»; можно оставить пустым', default: '' }
    ]);
    fullgram.ui.menu.add({ id: 'bookmark', title: 'В закладки', icon: 'bookmark.fill' });
    fullgram.on('menuAction', function (p) {
        if (!p || p.itemId !== 'bookmark') return;
        var tag = String(fullgram.settings.get('tag') || '').replace(/^[#\s]+|\s+$/g, '').toLowerCase().slice(0, 32);
        fullgram.messages.bookmarks.add({ peerId: p.peerId, messageId: Number(p.messageId), text: String(p.text || '').slice(0, 500), tag: tag });
        fullgram.toast(tag ? 'В закладках · #' + tag : 'В закладках');
    });
})();
