---
title: Совместимость с Remnawave
description: Что совместимо с экосистемой Remnawave и как это проверяется.
sidebar:
  order: 3
---

GoWave - замена бэкенда Remnawave, а не новая панель. Всё, что работает с Remnawave, должно работать и с GoWave.

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
