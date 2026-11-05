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
- Плагины на Lua, Python и Rust (WASM) / Plugins written in Lua, Python and Rust (WASM).
- Локальные инструменты для медиа, перевода и управления чатами / Local tools for media, translation and chat management.

## Иконки / App icons

В приложении ровно четыре варианта иконки / The app offers exactly four icons:

| Вариант / Variant | Русское название / Russian | English |
| --- | --- | --- |
| Белая / White | Белая | White |
| Оранжевая / Orange | Оранжевая | Orange |
| Красная / Red | Красная | Red |
| Маскот / Mascot | Маскот | Mascot |

Белая иконка используется по умолчанию. Исходные изображения находятся в
[assets/branding/source-artwork](assets/branding/source-artwork), а готовые
ресурсы — в [assets/branding](assets/branding) / White is the default icon.
Source artwork lives in [assets/branding/source-artwork](assets/branding/source-artwork)
and the prepared resources in [assets/branding](assets/branding).

## Структура / Layout

| Путь / Path | Назначение / Purpose |
| --- | --- |
| `patches/` | Патчи исходников iOS-клиента / Patches for the iOS client sources. |
| `ci/` | Подготовка исходников, проверки и сборка / Source preparation, checks and builds. |
| `assets/` | Иконки, шрифты и другие ресурсы / Icons, fonts and other resources. |
| `docs/` | Документация проекта / Project documentation. |

## Сборка / Building

Для нативной iOS-сборки нужны macOS и Xcode, совместимые с версией из
`upstream.json`. CI применяет патчи командой / A native iOS build needs macOS and
Xcode compatible with `upstream.json`. CI applies the patches with:

```sh
python3 ci/prepare.py telegram
```

Подробности — в [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) и
[TEST_RESULTS.md](TEST_RESULTS.md) / See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)
and [TEST_RESULTS.md](TEST_RESULTS.md) for details.

## Ссылки / Links

- Репозиторий / Repository: <https://github.com/KorsakovX/FullGram>
- Автор / Author: [ewwinc](https://github.com/ewwinc)

## Статус / Status

Версия 0.0.1. Перед установкой на устройство проверяйте результаты сборки,
подпись приложения и совместимость с вашей версией iOS. / Version 0.0.1. Before
installing on a device, verify the build output, the app signature and
compatibility with your iOS version.
