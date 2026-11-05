// ==FullGramPlugin==
// @id chat-statistics
// @name Статистика чата (вся история)
// @author Full Gram
// @version 1.0.0
// @description Пункт «Статистика чата» в меню сообщения: авторы, слова, часы и дни активности по всем сообщениям чата, сохранённым на устройстве.
// @permissions menu, messages.read
// ==/FullGramPlugin==

(function () {
    'use strict';
    fullgram.ui.menu.add({ id: 'chat-statistics', title: 'Статистика чата', icon: 'chart.bar.fill' });
    fullgram.on('menuAction', function (p) {
        if (!p || p.itemId !== 'chat-statistics') return;
        fullgram.tools.chatStats(p.peerId).catch(function (e) { fullgram.toast('Не удалось: ' + e.message); });
    });
})();
