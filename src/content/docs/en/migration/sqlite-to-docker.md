---
title: SQLite to Docker
description: Moving a GoWave SQLite installation to Docker with PostgreSQL in one command.
sidebar:
  order: 4
---

One command moves an SQLite installation into Docker. It needs Docker with the compose plugin; run it as root on the panel server:

```bash
gowave migrate to-docker
```

The command:

1. finds the current installation (`/opt/gowave`) and its `.env`, and checks SQLite for broken references between tables before changing anything;
2. creates `/opt/gowave-docker` with `docker-compose.yml` and `.env`, carrying over **the same** `APP_SECRET` and all settings, and generates a PostgreSQL password;
3. pulls the images, starts PostgreSQL, stops `gowave.service` and copies the data;
4. starts the panel in Docker on the same port and waits until it answers;
5. disables `gowave.service`; the `gowave` command then runs inside the container.

:::caution[APP_SECRET]
`APP_SECRET` is part of administrator password hashes, API tokens and the encryption of node SSH credentials. The command carries it over; if you move manually, use the same secret or you will not be able to log in.
:::

If any step fails, the Docker project is removed and the old panel is started again. The SQLite file is not modified, so you can also go back later:

```bash
cd /opt/gowave-docker && docker compose down
ln -sf /opt/gowave/gowave-server /usr/local/bin/gowave
systemctl enable --now gowave
```

Changes made in the panel after the move are not copied back to SQLite.

The move keeps the dashboard path (`PANEL_BASE_PATH`), credentials and subscription URLs. The new project's `.env` gets `GOWAVE_COMPOSE_DIR`, so the panel shows the right update command.

## Flags

| Flag | What it does |
| :--- | :--- |
| `--dir <path>` | Docker project directory, `/opt/gowave-docker` by default |
| `--image <image>` | Panel image, `ghcr.io/aaasazan/gowave:latest` by default. For the dev channel, `ghcr.io/aaasazan/gowave:dev` |
| `--from <path>` | Current installation directory, by default the one holding the binary |
| `--from-upstream [dsn]` | Copy the Remnawave database into the new PostgreSQL instead of GoWave's SQLite. Without a DSN it is found through `/opt/remnawave/.env`. This is how the installer moves Remnawave straight into Docker |
| `--yes` | Do not ask for confirmation |
