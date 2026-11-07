---
title: Logs
description: Where to find GoWave logs, what they contain and how to tune them.
sidebar:
  order: 3
---

## Where to look

| What | Command |
| :--- | :--- |
| Panel on systemd | `journalctl -u gowave -f` |
| Panel in Docker | `cd /opt/gowave-docker && docker compose logs -f gowave` |
| PostgreSQL in Docker | `docker compose logs -f postgres` |
| In-panel update | `journalctl -u gowave-update.service` |
| Installer | `/var/log/gowave-install.log` |
| Go node and Xray | `gowave-node logs -f` and `gowave-node xlogs -f`, see the [node CLI](../../install/node/cli/) |

## Format

One line per event: UTC time, level, the component in square brackets and the message. On startup the panel writes a summary that shows how it is configured:

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

The database password never reaches the log: the summary shows only the database address and name.

After that the log records what happens at runtime: nodes that drop and come back, sync errors, notifications that could not be delivered, update requests. When a background job fails, the log gets the first failure and the final give-up after all retries; the attempts in between show only at `debug` level.

## Settings

| Variable | What it changes |
| :--- | :--- |
| `LOG_LEVEL` | `debug`, `info` (default), `warn`, `error` |
| `LOG_FORMAT` | `text` (default) or `json` for Loki, Vector and other collectors. In JSON the component is the `component` field |
| `IS_HTTP_LOGGING_ENABLED` | `true` logs every HTTP request, subscription fetches included |

An unknown `LOG_LEVEL` or `LOG_FORMAT` does not stop the panel: it logs a warning and runs with `info` and `text`.

In Docker the logs are rotated: up to 5 files of 20 MB per container. On systemd, `journald` limits the log size.

## Startup warnings

| Message | Meaning |
| :--- | :--- |
| `[security] GoWave is running as root` | The service runs as root. Update the panel with the installer; it moves the service to the `gowave` user |
| `[security] ... is writable by the service account` | The panel itself could replace its binary. The installer gives it back to root |
| `[security] APP_HOST=... exposes the panel without HTTPS` | The panel listens on a non-loopback address. Keep `APP_HOST=127.0.0.1` and serve it through a reverse proxy (does not apply to Docker: `0.0.0.0` is required inside the container, and host access is restricted by publishing to `127.0.0.1` in compose) |
| `[http] No frontend build found` | There is no `frontend/dist` nearby, so only the API is served |
| `[jobs] ... failed for good` | Some background jobs (notifications, node sync) never completed |
