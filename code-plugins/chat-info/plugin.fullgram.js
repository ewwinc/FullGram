// ==FullGramPlugin==
// @id chat-info
// @name Инфа о чате
// @author Full Gram
// @version 1.0.0
// @description Пункт «Инфа о чате» в меню сообщения: количество сообщений, кружков и голосовых, самые частые и редкие слова, дата первого и последнего сообщения.
// @permissions menu, messages.read, ui
// ==/FullGramPlugin==

(function () {
    'use strict';

    var ITEM_ID = 'chat-info';
    var MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];

    fullgram.ui.menu.add({ id: ITEM_ID, title: 'Инфа о чате', icon: 'info.circle' });

    fullgram.on('menuAction', function (payload) {
        if (!payload || payload.itemId !== ITEM_ID) return;
        fullgram.messages.stats({ peerId: payload.peerId }).then(function (stats) {
            fullgram.ui.alert({
                title: 'Инфа о чате',
                message: format(stats || {}),
                buttons: [{ id: 'ok', title: 'Закрыть' }]
            });
        }, function (error) {
            fullgram.toast('Инфа о чате: ' + (error && error.message ? error.message : error));
        });
    });

    function formatNumber(value) {
        return String(Number(value) || 0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function pad(value) {
        return (value < 10 ? '0' : '') + value;
    }

    function formatDate(value) {
        if (value === null || value === undefined || value === '') return '—';
        var date = new Date(Number(value) * 1000);
        if (isNaN(date.getTime())) return '—';
        return date.getDate() + ' ' + MONTHS[date.getMonth()] + ' ' + date.getFullYear() + ', ' + pad(date.getHours()) + ':' + pad(date.getMinutes());
    }

    function words(list) {
        if (!list || !list.length) return '—';
        return list.map(function (item) {
            return item.word + ' — ' + formatNumber(item.count);
        }).join(', ');
    }

    function format(stats) {
        var count = Number(stats.count) || 0;
        var lines = [
            'Сообщений: ' + formatNumber(count),
            'Кружков: ' + formatNumber(stats.roundVideos),
            'Голосовых: ' + formatNumber(stats.voices),
            '',
            'Первое сообщение: ' + formatDate(stats.firstDate),
            'Последнее сообщение: ' + formatDate(stats.lastDate),
            '',
            'Самые частые слова:',
            words(stats.frequentWords),
            '',
            'Самые редкие слова:',
            words(stats.rareWords)
        ];
        var sample = Number(stats.wordSampleSize) || 0;
        if (sample > 0 && sample < count) {
            lines.push('', 'Слова посчитаны по последним ' + formatNumber(sample) + ' сообщениям.');
        }
        if (stats.truncated) {
            lines.push('', 'Учтены не все сохранённые сообщения.');
        }
        return lines.join('\n');
    }
})();
