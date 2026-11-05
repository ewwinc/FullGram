// ==FullGramPlugin==
// @id describe-photo
// @name Описать фото
// @author Full Gram
// @version 1.0.0
// @description Пункт «Описать фото» в меню сообщения с фото: что на снимке и какой на нём текст. Распознаётся на устройстве, фото никуда не отправляется.
// @permissions menu, ui, messages.read
// ==/FullGramPlugin==

(function () {
    'use strict';
    fullgram.ui.menu.add({ id: 'describe-photo', title: 'Описать фото', icon: 'text.viewfinder', media: 'photo' });
    fullgram.on('menuAction', function (p) {
        if (!p || p.itemId !== 'describe-photo') return;
        fullgram.media.describePhoto(p.peerId, p.messageId).then(function (text) {
            fullgram.ui.alert({ title: 'Описание', message: text || 'Ничего не распознано.', buttons: [{ id: 'ok', title: 'OK' }] });
        }).catch(function (e) { fullgram.toast('Не удалось: ' + e.message); });
    });
})();
