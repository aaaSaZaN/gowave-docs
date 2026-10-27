---
title: Сравнение с Remnawave
description: Чем GoWave отличается от оригинального бэкенда Remnawave.
sidebar:
  order: 3
---

GoWave заменяет бэкенд Remnawave и держит его API. Различия в том, как он устроен внутри и что добавлено сверху.

| | GoWave | Remnawave |
| :--- | :--- | :--- |
| Язык | Go | TypeScript (Node.js) |
| Процессы | Один | Три: API, обработчики очередей, планировщик |
| База данных | SQLite или PostgreSQL | PostgreSQL и Valkey (Redis) |
| Память под нагрузкой | около 60 МБ | около 1 ГБ |
| Готовность API после запуска | 0,21 с | 7,1 с |
| API | Все 218 команд `@remnawave/backend-contract` 3.4.15 | Эталон |
| Веб-интерфейс | Интерфейс Remnawave | Свой |
| Ноды | Go-нода и `remnawave/node` | `remnawave/node`, Go-нода тоже подключается |
| Установка | Установщик одной командой, бинарник или Docker | Docker Compose |
| Обновление | Кнопкой в панели (systemd) или `docker compose pull` | `docker compose pull` |

Память и время запуска измерены на одинаковом стенде, методика на странице [бенчмарков](../../benchmarks/).

## Что есть только в GoWave

- Работа без Docker: один бинарник и база SQLite.
- [Установщик](../../overview/quick-start/), который сам настраивает HTTPS и переносит данные с Remnawave и PasarGuard.
- [Переход с SQLite на PostgreSQL](../../migration/sqlite-to-docker/) одной командой с откатом при ошибке.
- Перенос из [PasarGuard](../../migration/pasarguard/).

## Что работает иначе

- **Регулярные выражения** в [правилах ответа](../../features/subscription-rules/) и [шаблонах](../../features/templates/) работают в синтаксисе RE2 (Go), а не JavaScript. Lookahead, lookbehind и обратные ссылки не поддерживаются. Правило Remnawave с такими конструкциями в GoWave перестанет совпадать.
- **Обновление в Docker** не запускается из панели: она показывает команду для сервера, см. [обновление](../../install/updating/).

## Что совместимо

- **API.** Эндпоинты, форматы запросов и ответов, коды ошибок и статусы соответствуют `@remnawave/backend-contract`. Веб-интерфейс - фронтенд Remnawave.
- **Подписки.** Выдача для Xray JSON, Mihomo, sing-box, base64 и остальных клиентов сверяется с эталонным выводом оригинального бэкенда.
- **Ноды.** Оригинальная нода `remnawave/node` и [Go-нода](../../install/node/install/).
- **Страница подписки** `remnawave/subscription-page`.
- **Боты и интеграции**, которые ходят в API Remnawave по токену.

## Что GoWave добавляет к API

Эндпоинты сверх контракта нужны веб-интерфейсу GoWave, клиенты и боты Remnawave их не вызывают. В [справочнике API](../../api/) они собраны в разделе **GoWave extensions**:

- `GET /api/nodes/traffic-summary` - трафик каждой ноды за всё время, ежемесячный сброс его не обнуляет;
- `GET /api/nodes/{uuid}/logs`, `GET /api/nodes/{uuid}/updates` и `POST /api/nodes/{uuid}/updates/apply` - логи и обновление [Go-ноды](../../install/node/cli/);
- `GET /api/system/updates/check` и `POST /api/system/updates/apply` - [обновление панели](../../install/updating/) на systemd;
- `POST /api/system/actions/restore` - восстановление из бэкапа.

В `PATCH /api/nodes` есть поле `trafficTrackingStart`, которого нет в контракте. Оно задаёт, с чего начнётся счётчик, когда обновление включает учёт трафика: `keep` оставляет накопленное с последнего сброса (так делает Remnawave), `zero` начинает с нуля, `period` пересчитывает текущий период по истории.

Вход через Яндекс удалён. Поля `yandex` в настройках OAuth остались ради совместимости с контрактом, но провайдер всегда выключен, а сохранённые ключи панель отбрасывает.

## Как это проверяется

- Тесты сверяют список маршрутов с контрактом и проверяют реальные ответы обработчиков JSON-схемами контракта - на SQLite и на PostgreSQL, в каждом CI.
- Вывод подписок сравнивается с зафиксированными эталонами, снятыми с оригинального бэкенда.

## Где что описано

Подписки GoWave описаны здесь: [правила ответа](../../features/subscription-rules/), [шаблоны Xray JSON, Mihomo и sing-box](../../features/templates/), [переменные](../../features/template-variables/). Профили конфигурации устроены как обычные конфиги Xray, поэтому протоколы и транспорты настраиваются по [документации Xray](https://xtls.github.io/config/).
