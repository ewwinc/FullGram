# Full Gram 0.0.1

Full Gram — модификация Telegram для iOS с дополнительными настройками интерфейса,
приватности, оформления и плагинов.

Full Gram is a Telegram modification for iOS with extra interface, privacy,
appearance and plugin settings.

## Возможности / Features

- Ghost Mode и расширенные параметры приватности / Ghost Mode and extended privacy controls.
- Локальная история изменений и удалённых сообщений / Local history of edits and deleted messages.
- Фильтры, инструменты форматирования и расширенное меню сообщений / Filters, formatting tools and an expanded message menu.
- Настройки внешнего вида, темы и четыре варианта иконки / Appearance settings, themes and four app icons.
- Плагины на JavaScript, Lua, Python и Rust (WASM) / Plugins written in JavaScript, Lua, Python and Rust (WASM).
- Первый JS-плагин «Инфа о чате»: статистика чата из меню сообщения / First JS plugin “Chat info”: chat statistics from the message menu.
- Локальные инструменты для медиа, перевода и управления чатами / Local tools for media, translation and chat management.

## Иконки / App icons

В приложении ровно четыре варианта иконки / The app offers exactly four icons:

| Вариант / Variant | Русское название / Russian | English |
| --- | --- | --- |
| Белая / White | Белая | White |
| Оранжевая / Orange | Оранжевая | Orange |
| Красная / Red | Красная | Red |
| runa | runa | runa |

Белая иконка используется по умолчанию. Исходные изображения находятся в
`assets/branding/source-artwork`, готовые ресурсы — в `assets/branding` /
White is the default icon. Source artwork lives in
`assets/branding/source-artwork` and the prepared resources in
`assets/branding`.

## Версия 0.0.1 / Version 0.0.1

Текущая версия — 0.0.1. Что изменилось / Current release is 0.0.1. Highlights:

- Ровно четыре иконки: Белая, Оранжевая, Красная и runa / Exactly four icons:
  White, Orange, Red and runa.
- Менеджер плагинов показывает только код-плагины: без каталога, бейджей и
  тегов BETA/ALPHA / The plugin manager shows code plugins only: no catalog,
  badges or BETA/ALPHA tags.
- Первый JS-плагин «Инфа о чате» открывается из меню долгого нажатия на
  сообщение / The first JS plugin, “Chat info”, opens from the message
  long-press menu.
- Плагин показывает количество сообщений, голосовых и кружков, самые частые и
  самые редкие слова, дату первого и дату со временем последнего сообщения /
  The plugin reports message, voice and round-video counts, the most and least
  frequent words, and the date of the first and last message.
- Статистика считается нативно и не зависит от загруженной истории на экране /
  Statistics are computed natively and do not depend on the history loaded on
  screen.

## Структура / Layout

| Путь / Path | Назначение / Purpose |
| --- | --- |
| `patches/` | Патчи исходников iOS-клиента / Patches for the iOS client sources. |
| `ci/` | Подготовка исходников, проверки и сборка / Source preparation, checks and builds. |
| `assets/` | Иконки, шрифты и другие ресурсы / Icons, fonts and other resources. |
| `docs/` | Документация проекта / Project documentation. |

## Статус / Status

Версия 0.0.1. Перед установкой на устройство проверяйте подпись приложения и
совместимость с вашей версией iOS. / Version 0.0.1. Before installing on a
device, verify the app signature and compatibility with your iOS version.

Автор / Author: ewwinc.
