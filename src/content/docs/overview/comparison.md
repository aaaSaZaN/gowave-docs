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
| Готовность API после запуска | 0,15 с | 4,3 с |
| API | Все 218 команд `@remnawave/backend-contract` 3.4.15 | Эталон |
| Веб-интерфейс | Интерфейс Remnawave | Свой |
| Ноды | Go-нода и `remnawave/node` | `remnawave/node`, Go-нода тоже подключается |
| Установка | Установщик одной командой, бинарник или Docker | Docker Compose |
| Обновление | Кнопкой в панели (systemd) или `docker compose pull` | `docker compose pull` |

Память и время запуска измерены на одинаковом стенде, методика на странице [бенчмарков](../../benchmarks/).

## Что есть только в GoWave

- Работа без Docker: один бинарник и база SQLite.
- [Установщик](../../install/installer/), который сам настраивает HTTPS и переносит данные с Remnawave и PasarGuard.
- [Переход с SQLite на PostgreSQL](../../migration/sqlite-to-docker/) одной командой с откатом при ошибке.
- Перенос из [PasarGuard](../../migration/pasarguard/).

## Что работает иначе

- **Регулярные выражения** в [правилах ответа](../../features/subscription-rules/) и [шаблонах](../../features/templates/) работают в синтаксисе RE2 (Go), а не JavaScript. Lookahead, lookbehind и обратные ссылки не поддерживаются. Правило Remnawave с такими конструкциями в GoWave перестанет совпадать.
- **Обновление в Docker** не запускается из панели: она показывает команду для сервера, см. [обновление](../../install/updating/).

## Как проверяется совместимость

Тесты сверяют маршруты с контрактом и проверяют ответы JSON-схемами контракта на SQLite и PostgreSQL. Вывод подписок сравнивается с эталонами, снятыми с оригинального бэкенда, подробности в разделе [совместимость](../../reference/compatibility/).
