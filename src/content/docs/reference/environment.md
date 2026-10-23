---
title: Переменные окружения
description: Все настройки GoWave из .env.
sidebar:
  order: 2
---

Настройки читаются из `.env` в рабочей папке (и из `../.env`) или из окружения процесса. Некорректные значения не принимаются: панель не запустится и напишет, какая переменная неверна.

## Основные

| Переменная | По умолчанию | Описание |
| :--- | :--- | :--- |
| `APP_SECRET` | *обязательно* | Секрет не короче 32 символов. Подписывает JWT и участвует в хешах паролей, API-токенах и шифровании SSH-данных нод - не меняйте его на работающей панели |
| `APP_HOST` | `127.0.0.1` | Адрес, на котором слушают панель и метрики. Наружу панель отдаётся через reverse proxy с HTTPS; `0.0.0.0` нужен только внутри контейнера |
| `APP_PORT` | `3000` | Порт панели и API |
| `PANEL_DOMAIN` | `localhost:3000` | Домен панели |
| `SUB_PUBLIC_DOMAIN` | `localhost:3000/api/sub` | Публичный адрес подписок |
| `FRONT_END_DOMAIN` | `*` | Разрешённые домены для CORS |
| `JWT_AUTH_LIFETIME` | `12` | Срок жизни сессии администратора, часы |
| `SHORT_UUID_LENGTH` | `16` | Длина короткого UUID подписки, 16-64 |

## База данных

| Переменная | По умолчанию | Описание |
| :--- | :--- | :--- |
| `DB_DRIVER` | `sqlite` | `sqlite` или `postgres`. Если не задан, а `DATABASE_URL` начинается с `postgres://`, выбирается PostgreSQL |
| `DATABASE_URL` | `gowave.db` | Путь к файлу SQLite или DSN PostgreSQL |
| `DB_MAX_CONNECTIONS` | `20` | Размер пула соединений PostgreSQL, 1-500. Каждое соединение - отдельный процесс PostgreSQL на несколько МБ; 20 хватает даже под нагрузкой бенчмарка |

## Метрики

| Переменная | По умолчанию | Описание |
| :--- | :--- | :--- |
| `METRICS_PORT` | `3001` | Порт Prometheus-метрик |
| `METRICS_USER`, `METRICS_PASS` | не заданы | Basic auth для `/metrics` |

## Поведение сервиса

| Переменная | По умолчанию | Описание |
| :--- | :--- | :--- |
| `SERVICE_CLEAN_USAGE_HISTORY` | `false` | Очищать историю использования |
| `SERVICE_DISABLE_USER_USAGE_RECORDS` | `false` | Не записывать статистику трафика по пользователям |
| `SERVICE_DISABLE_SRH_RECORDS` | `false` | Не записывать историю запросов подписки |
| `USER_USAGE_IGNORE_BELOW_BYTES` | `0` | Не учитывать трафик меньше этого значения |
| `EXPORT_TO_STREAM_ENABLED` | `false` | Экспорт событий в поток |

## Уведомления

### Вебхуки

| Переменная | Описание |
| :--- | :--- |
| `WEBHOOK_ENABLED` | `true`, чтобы включить |
| `WEBHOOK_URL` | Один или несколько адресов через запятую, `http://` или `https://` |
| `WEBHOOK_SECRET_HEADER` | Не короче 32 латинских букв и цифр; обязателен при включённых вебхуках |

### Telegram

| Переменная | Описание |
| :--- | :--- |
| `IS_TELEGRAM_NOTIFICATIONS_ENABLED` | `true`, чтобы включить |
| `TELEGRAM_BOT_TOKEN` | Токен бота; обязателен при включённых уведомлениях |
| `TELEGRAM_BOT_API_ROOT` | Свой Bot API сервер (по умолчанию `https://api.telegram.org`) |
| `TELEGRAM_BOT_PROXY` | Прокси для запросов к Telegram |
| `TELEGRAM_NOTIFY_USERS` | Чат для событий пользователей: `chatId` или `chatId:threadId` |
| `TELEGRAM_NOTIFY_NODES` | Чат для событий нод |
| `TELEGRAM_NOTIFY_SERVICE` | Чат для сервисных событий и ошибок |
| `TELEGRAM_NOTIFY_CRM` | Чат для событий CRM |
| `TELEGRAM_NOTIFY_TBLOCKER` | Чат для Torrent Blocker |

Чат со значением `change_me` считается ненастроенным. Кнопка «View user» в отчётах Torrent Blocker ведёт на `PANEL_DOMAIN` с учётом `PANEL_BASE_PATH` и не добавляется, если домен локальный. При неудачном входе в Telegram уходит только длина введённого пароля, сам пароль не отправляется.

Настройки уведомлений старой панели переносятся при миграции автоматически. На уже установленной GoWave их можно перенести пунктом меню установщика «Перенести уведомления Telegram и вебхуки из старой панели».

### Пороговые уведомления

Списки задаются JSON-массивом чисел, например `[60, 80, 95]`, и действуют только при включённом флаге:

| Флаг | Список |
| :--- | :--- |
| `BANDWIDTH_USAGE_NOTIFICATIONS_ENABLED` | `BANDWIDTH_USAGE_NOTIFICATIONS_THRESHOLD` - проценты лимита трафика |
| `NOT_CONNECTED_USERS_NOTIFICATIONS_ENABLED` | `NOT_CONNECTED_USERS_NOTIFICATIONS_AFTER_HOURS` - часы без подключения |
| `EXPIRATION_NOTIFICATIONS_ENABLED` | `EXPIRATION_NOTIFICATIONS` - когда предупреждать об окончании подписки |

## Docker

Только для [compose-установки](../../install/docker/):

| Переменная | Описание |
| :--- | :--- |
| `GOWAVE_IMAGE` | Образ панели, по умолчанию `ghcr.io/aaasazan/gowave:latest` |
| `GOWAVE_COMPOSE_DIR` | Папка с `docker-compose.yml`; используется в подсказке обновления |
| `POSTGRES_USER`, `POSTGRES_DB` | По умолчанию `gowave` |
| `POSTGRES_PASSWORD` | Обязателен |
| `POSTGRES_PORT` | Порт PostgreSQL на `127.0.0.1`, по умолчанию `5432` |
