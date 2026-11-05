// ==FullGramPlugin==
// @id year-in-review
// @name Итоги года
// @author Full Gram
// @version 1.0.0
// @description Пункт «Итоги года» в меню сообщения: сколько вы переписывались в этом чате с 1 января, самые активные месяцы и дни.
// @permissions menu, messages.read
// ==/FullGramPlugin==

(function () {
    'use strict';
    fullgram.ui.menu.add({ id: 'year-in-review', title: 'Итоги года', icon: 'calendar.badge.clock' });
    fullgram.on('menuAction', function (p) {
        if (!p || p.itemId !== 'year-in-review') return;
        fullgram.tools.yearInReview(p.peerId).catch(function (e) { fullgram.toast('Не удалось: ' + e.message); });
    });
})();
