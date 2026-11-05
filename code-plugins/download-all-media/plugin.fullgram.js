// ==FullGramPlugin==
// @id download-all-media
// @name Скачать все медиа
// @author Full Gram
// @version 1.0.0
// @description Пункт «Скачать все медиа» в меню сообщения: сохраняет фото, видео и файлы чата (до 500 последних) в одну папку.
// @permissions menu, messages.read
// ==/FullGramPlugin==

(function () {
    'use strict';
    fullgram.ui.menu.add({ id: 'download-all-media', title: 'Скачать все медиа', icon: 'square.and.arrow.down.on.square.fill' });
    fullgram.on('menuAction', function (p) {
        if (!p || p.itemId !== 'download-all-media') return;
        fullgram.tools.downloadChatMedia(p.peerId).catch(function (e) { fullgram.toast('Не удалось: ' + e.message); });
    });
})();
