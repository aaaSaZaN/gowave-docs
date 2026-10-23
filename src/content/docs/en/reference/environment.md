---
title: Environment variables
description: Every GoWave setting from .env.
sidebar:
  order: 2
---

Settings are read from `.env` in the working directory (and `../.env`) or from the process environment. Invalid values are rejected: the panel refuses to start and names the wrong variable.

## Core

| Variable | Default | Description |
| :--- | :--- | :--- |
| `APP_SECRET` | *required* | Secret of at least 32 characters. Signs JWTs and is part of password hashes, API tokens and node SSH credential encryption, so do not change it on a running panel |
| `APP_HOST` | `127.0.0.1` | Address the panel and metrics listen on. Expose the panel through a reverse proxy with HTTPS; `0.0.0.0` is only needed inside a container |
| `APP_PORT` | `3000` | Panel and API port |
| `PANEL_DOMAIN` | `localhost:3000` | Panel domain |
| `SUB_PUBLIC_DOMAIN` | `localhost:3000/api/sub` | Public subscription address |
| `FRONT_END_DOMAIN` | `*` | Allowed CORS origins |
| `JWT_AUTH_LIFETIME` | `12` | Administrator session lifetime, hours |
| `SHORT_UUID_LENGTH` | `16` | Subscription short UUID length, 16 to 64 |

## Database

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DB_DRIVER` | `sqlite` | `sqlite` or `postgres`. When unset and `DATABASE_URL` starts with `postgres://`, PostgreSQL is used |
| `DATABASE_URL` | `gowave.db` | SQLite file path or PostgreSQL DSN |
| `DB_MAX_CONNECTIONS` | `20` | PostgreSQL pool size, 1 to 500. Each connection is a separate PostgreSQL process of a few MB; 20 is enough even under benchmark load |

## Metrics

| Variable | Default | Description |
| :--- | :--- | :--- |
| `METRICS_PORT` | `3001` | Prometheus metrics port |
| `METRICS_USER`, `METRICS_PASS` | not set | Basic auth for `/metrics` |

## Service behaviour

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SERVICE_CLEAN_USAGE_HISTORY` | `false` | Clean usage history |
| `SERVICE_DISABLE_USER_USAGE_RECORDS` | `false` | Do not record per-user traffic statistics |
| `SERVICE_DISABLE_SRH_RECORDS` | `false` | Do not record subscription request history |
| `USER_USAGE_IGNORE_BELOW_BYTES` | `0` | Ignore traffic below this value |
| `EXPORT_TO_STREAM_ENABLED` | `false` | Export events to a stream |

## Notifications

### Webhooks

| Variable | Description |
| :--- | :--- |
| `WEBHOOK_ENABLED` | `true` to enable |
| `WEBHOOK_URL` | One or more comma-separated `http://` or `https://` URLs |
| `WEBHOOK_SECRET_HEADER` | At least 32 Latin letters and digits; required when webhooks are enabled |

### Telegram

| Variable | Description |
| :--- | :--- |
| `IS_TELEGRAM_NOTIFICATIONS_ENABLED` | `true` to enable |
| `TELEGRAM_BOT_TOKEN` | Bot token; required when notifications are enabled |
| `TELEGRAM_BOT_API_ROOT` | Custom Bot API server (default `https://api.telegram.org`) |
| `TELEGRAM_BOT_PROXY` | Proxy for Telegram requests |
| `TELEGRAM_NOTIFY_USERS` | Chat for user events: `chatId` or `chatId:threadId` |
| `TELEGRAM_NOTIFY_NODES` | Chat for node events |
| `TELEGRAM_NOTIFY_SERVICE` | Chat for service events and errors |
| `TELEGRAM_NOTIFY_CRM` | Chat for CRM events |
| `TELEGRAM_NOTIFY_TBLOCKER` | Chat for Torrent Blocker |

A chat set to `change_me` counts as not configured. The "View user" button in Torrent Blocker reports points to `PANEL_DOMAIN` with `PANEL_BASE_PATH` and is omitted for local domains. A failed login sends only the length of the typed password to Telegram, never the password itself.

Notification settings of the old panel are copied during migration. On an existing GoWave install, use the installer menu item "Copy Telegram and webhook notifications from the old panel".

### Threshold notifications

Lists are JSON number arrays such as `[60, 80, 95]` and only apply when their flag is on:

| Flag | List |
| :--- | :--- |
| `BANDWIDTH_USAGE_NOTIFICATIONS_ENABLED` | `BANDWIDTH_USAGE_NOTIFICATIONS_THRESHOLD`: percent of the traffic limit |
| `NOT_CONNECTED_USERS_NOTIFICATIONS_ENABLED` | `NOT_CONNECTED_USERS_NOTIFICATIONS_AFTER_HOURS`: hours without connecting |
| `EXPIRATION_NOTIFICATIONS_ENABLED` | `EXPIRATION_NOTIFICATIONS`: when to warn about subscription expiry |

## Docker

For the [compose installation](../../install/docker/) only:

| Variable | Description |
| :--- | :--- |
| `GOWAVE_IMAGE` | Panel image, default `ghcr.io/aaasazan/gowave:latest` |
| `GOWAVE_COMPOSE_DIR` | Directory with `docker-compose.yml`; shown in the update hint |
| `POSTGRES_USER`, `POSTGRES_DB` | Default `gowave` |
| `POSTGRES_PASSWORD` | Required |
| `POSTGRES_PORT` | PostgreSQL port on `127.0.0.1`, default `5432` |
