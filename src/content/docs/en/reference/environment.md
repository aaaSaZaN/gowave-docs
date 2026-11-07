---
title: Environment variables
description: Every GoWave setting from .env.
sidebar:
  order: 2
---

Settings are read from `.env` in the working directory (and `../.env`) or from the process environment. Invalid values are rejected: the panel refuses to start and names the wrong variable. After changing `.env`, restart the panel: `systemctl restart gowave` or `docker compose up -d`.

## Core

| Variable | Default | Description |
| :--- | :--- | :--- |
| `APP_SECRET` | *required* | Secret of at least 32 characters. Signs JWTs and is part of password hashes, API tokens and node SSH credential encryption, so do not change it on a running panel |
| `APP_HOST` | `127.0.0.1` | Address the panel and metrics listen on. Expose the panel through a reverse proxy with HTTPS; `0.0.0.0` is only needed inside a container. Any other address works but logs a warning |
| `APP_PORT` | `3000` | Panel and API port |
| `PANEL_DOMAIN` | `localhost:3000` | Panel domain |
| `PANEL_BASE_PATH` | `/` | Dashboard path, for example `/private/panel/`. The API, subscriptions and metrics keep their addresses. See the [installer](../../install/installer/#dashboard-path) |
| `SUB_PUBLIC_DOMAIN` | `localhost:3000/api/sub` | Public subscription address, without `https://` or a trailing `/` |
| `FRONT_END_DOMAIN` | `*` | Allowed CORS origins |
| `JWT_AUTH_LIFETIME` | `12` | Administrator session lifetime, hours |
| `SHORT_UUID_LENGTH` | `16` | Subscription short UUID length, 16 to 64 |

## Database

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DB_DRIVER` | `sqlite` | `sqlite` or `postgres`. When unset and `DATABASE_URL` starts with `postgres://` or `postgresql://`, PostgreSQL is used |
| `DATABASE_URL` | `gowave.db` | SQLite file path or PostgreSQL DSN |
| `DB_MAX_CONNECTIONS` | `20` | PostgreSQL pool size, 1 to 500. Each connection is a separate PostgreSQL process of a few MB; 20 is enough even under benchmark load |

## Log

| Variable | Default | Description |
| :--- | :--- | :--- |
| `LOG_LEVEL` | `info` | `debug`, `info`, `warn` or `error` |
| `LOG_FORMAT` | `text` | `text` for `journalctl` and `docker compose logs`, `json` for log collectors |
| `IS_HTTP_LOGGING_ENABLED` | `false` | Log every HTTP request, subscription fetches included. On a busy panel that is a lot of lines |

What goes into the log and how to read it: see [Logs](../logs/).

## Metrics

| Variable | Default | Description |
| :--- | :--- | :--- |
| `METRICS_ENABLED` | `true` | `false` keeps the metrics port closed. The systemd installer writes `false` |
| `METRICS_PORT` | `3001` | Prometheus metrics port, listens on `APP_HOST` |
| `METRICS_USER`, `METRICS_PASS` | not set | Basic auth for `/metrics`. Until both are set, `/metrics` always answers 401 |

The metrics port also serves `/health`, which checks the database connection and needs no password. Any other path on that port drops the connection.

## Service behaviour

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SERVICE_CLEAN_USAGE_HISTORY` | `false` | Once a week (Monday, 00:30 UTC) wipe the per-node user traffic history |
| `SERVICE_DISABLE_USER_USAGE_RECORDS` | `false` | Do not record per-user traffic statistics |
| `SERVICE_DISABLE_SRH_RECORDS` | `false` | Do not record subscription request history |
| `USER_USAGE_IGNORE_BELOW_BYTES` | `0` | Skip a user's traffic for a polling round if it is below this many bytes |
| `EXPORT_TO_STREAM_ENABLED` | `false` | A compatibility flag only: the API reports its value, but GoWave has no Redis Streams export |

## Notifications

How webhooks work and how to turn single events on or off: see [Notifications](../../features/notifications/).

### Webhooks

| Variable | Description |
| :--- | :--- |
| `WEBHOOK_ENABLED` | `true` to enable |
| `WEBHOOK_URL` | One or more comma-separated `http://` or `https://` URLs |
| `WEBHOOK_SECRET_HEADER` | At least 32 Latin letters and digits; required when webhooks are enabled. Every request is signed with it |

### Telegram

| Variable | Description |
| :--- | :--- |
| `IS_TELEGRAM_NOTIFICATIONS_ENABLED` | `true` to enable |
| `TELEGRAM_BOT_TOKEN` | Bot token; required when notifications are enabled |
| `TELEGRAM_BOT_API_ROOT` | Custom Bot API server (default `https://api.telegram.org`) |
| `TELEGRAM_BOT_PROXY` | Proxy for Telegram requests, for example `socks5://proxy:1080` |
| `TELEGRAM_NOTIFY_USERS` | Chat for user events: `chatId` or `chatId:threadId` |
| `TELEGRAM_NOTIFY_NODES` | Chat for node events |
| `TELEGRAM_NOTIFY_SERVICE` | Chat for service events and errors |
| `TELEGRAM_NOTIFY_CRM` | Chat for CRM events |
| `TELEGRAM_NOTIFY_TBLOCKER` | Chat for Torrent Blocker |

A chat set to `change_me` counts as not configured. The "View user" button in Torrent Blocker reports points to `PANEL_DOMAIN` with `PANEL_BASE_PATH` and is omitted for local domains. A failed login sends only the length of the typed password to Telegram, never the password itself.

Notification settings of the old panel are copied during migration. On an existing GoWave install, use the installer menu item "Copy Telegram and webhook notifications from the old panel".

### Threshold notifications

Lists are JSON number arrays such as `[60, 80, 95]` and only apply when their flag is on. With the flag on, an empty or non-JSON list stops the panel from starting.

| Flag | List |
| :--- | :--- |
| `BANDWIDTH_USAGE_NOTIFICATIONS_ENABLED` | `BANDWIDTH_USAGE_NOTIFICATIONS_THRESHOLD`: percent of the traffic limit |
| `NOT_CONNECTED_USERS_NOTIFICATIONS_ENABLED` | `NOT_CONNECTED_USERS_NOTIFICATIONS_AFTER_HOURS`: hours after the user was created without a connection |
| `EXPIRATION_NOTIFICATIONS_ENABLED` | `EXPIRATION_NOTIFICATIONS`: hours relative to expiry, negative before and positive after, for example `[-72, -24, 24]` |

### Events file

| Variable | Description |
| :--- | :--- |
| `NOTIFICATIONS_CONFIG_PATH` | Path to `notifications-config.yml`, which turns single events on or off. Without it the panel looks in the standard places, see [Notifications](../../features/notifications/#per-event-settings) |

## Docker

For the [compose installation](../../install/docker/) only:

| Variable | Description |
| :--- | :--- |
| `GOWAVE_IMAGE` | Panel image, default `ghcr.io/aaasazan/gowave:latest`. For the dev channel use `ghcr.io/aaasazan/gowave:dev` |
| `GOWAVE_COMPOSE_DIR` | Directory with `docker-compose.yml`; shown in the update hint |
| `POSTGRES_USER`, `POSTGRES_DB` | Default `gowave` |
| `POSTGRES_PASSWORD` | Required |
| `POSTGRES_PORT` | PostgreSQL port on `127.0.0.1`, default `5432` |
| `IN_DOCKER` | Set by the image. It tells the panel it runs in a container, so it shows a command instead of the update button |

The installer also writes `GOWAVE_PROXY` (`caddy`, `nginx` or `external`) to `.env` to remember which proxy it set up. The panel itself does not read it.

## What GoWave ignores

GoWave silently skips these variables from a Remnawave `.env`, because it needs neither Redis nor several processes:

- `REDIS_SOCKET`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD`;
- `API_INSTANCES`;
- `EXPORT_TO_STREAM_MAXLEN`;
- `SHORT_UUID_METHOD` and `SHORT_UUID_CUSTOM_PATTERN`: the short UUID is always a random string of `SHORT_UUID_LENGTH` characters.

A migrated `.env` with them still works; those lines just have no effect.
