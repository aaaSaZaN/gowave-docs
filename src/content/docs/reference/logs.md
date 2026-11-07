---
title: Журнал
description: Где смотреть логи GoWave, что в них пишется и как настроить подробность.
sidebar:
  order: 3
---

## Где смотреть

| Что | Команда |
| :--- | :--- |
| Панель на systemd | `journalctl -u gowave -f` |
| Панель в Docker | `cd /opt/gowave-docker && docker compose logs -f gowave` |
| PostgreSQL в Docker | `docker compose logs -f postgres` |
| Обновление из панели | `journalctl -u gowave-update.service` |
| Установщик | `/var/log/gowave-install.log` |
| Go-нода и Xray | `gowave-node logs -f` и `gowave-node xlogs -f`, см. [CLI ноды](../../install/node/cli/) |

## Формат

Одна строка на событие: время в UTC, уровень, компонент в квадратных скобках и сообщение. При запуске панель пишет сводку, по которой видно, как она настроена:

```text
2026-11-05 10:00:00.120 INFO  [startup] GoWave v1.2.3 starting (stable channel, go1.27.1, linux/amd64, pid 1234)
2026-11-05 10:00:00.180 INFO  [database] Connected to SQLite /opt/gowave/gowave.db; schema has 8 migrations, 0 applied now (12ms)
2026-11-05 10:00:00.181 INFO  [startup] Running as gowave (native service), timezone UTC
2026-11-05 10:00:00.181 INFO  [http] Dashboard served from /opt/gowave/frontend/dist at base path /
2026-11-05 10:00:00.181 INFO  [http] Panel domain panel.example.com, subscription domain panel.example.com/api/sub, HTTP access log off
2026-11-05 10:00:00.181 INFO  [metrics] Prometheus metrics disabled
2026-11-05 10:00:00.181 INFO  [telegram] Telegram notifications off (IS_TELEGRAM_NOTIFICATIONS_ENABLED)
2026-11-05 10:00:00.181 INFO  [webhook] Webhooks off (WEBHOOK_ENABLED)
2026-11-05 10:00:00.185 INFO  [startup] 120 users (97 active), 3 nodes (3 enabled)
2026-11-05 10:00:00.185 INFO  [jobs] 0 background jobs queued
2026-11-05 10:00:00.190 INFO  [http] GoWave v1.2.3 is ready on http://127.0.0.1:3000
```

Пароль базы в журнал не попадает: в сводке видны только адрес и имя базы.

Дальше в журнале появляются события работы: ноды, которые пропали и вернулись, ошибки синхронизации, уведомления, которые не удалось доставить, запросы обновления. Если фоновая задача не удалась, в журнал пишется первая неудача и окончательный отказ после всех повторов, промежуточные попытки видны только на уровне `debug`.

## Настройка

| Переменная | Что меняет |
| :--- | :--- |
| `LOG_LEVEL` | `debug`, `info` (по умолчанию), `warn`, `error` |
| `LOG_FORMAT` | `text` (по умолчанию) или `json` для Loki, Vector и других сборщиков. В JSON компонент лежит в поле `component` |
| `IS_HTTP_LOGGING_ENABLED` | `true` пишет каждый HTTP-запрос, включая запросы подписок |

Неизвестное значение `LOG_LEVEL` или `LOG_FORMAT` не останавливает панель: она пишет предупреждение и работает с `info` и `text`.

В Docker логи ротируются: до 5 файлов по 20 МБ на контейнер. На systemd размер журнала ограничивает `journald`.

## Предупреждения при запуске

| Сообщение | Что значит |
| :--- | :--- |
| `[security] GoWave is running as root` | Служба запущена от root. Обновите панель через установщик, он переведёт её на пользователя `gowave` |
| `[security] ... is writable by the service account` | Бинарник может изменить сама панель. Установщик вернёт его во владение root |
| `[security] APP_HOST=... exposes the panel without HTTPS` | Панель слушает не на loopback. Оставьте `APP_HOST=127.0.0.1` и отдавайте её через reverse proxy (к Docker это не относится: внутри контейнера `0.0.0.0` необходим, а доступ ограничивается публикацией на `127.0.0.1` в compose-файле) |
| `[http] No frontend build found` | Рядом нет `frontend/dist`, работает только API |
| `[jobs] ... failed for good` | Часть фоновых задач (уведомления, синхронизация нод) так и не выполнилась |
