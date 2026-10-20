---
title: Docker Compose and PostgreSQL
description: Manual GoWave installation in Docker with PostgreSQL 18.
sidebar:
  order: 2
---

The panel image is published as `ghcr.io/aaasazan/gowave` for `linux/amd64` and `linux/arm64`.

## Docker

If Docker is not installed yet, use the official script. It installs Docker Engine and the `docker compose` plugin:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

:::note[Why "not for production"]
Docker calls this the *convenience script*: it installs the latest version without asking and is not meant to upgrade an existing installation. For a single panel VPS it is fine: it adds Docker's official repository, so Docker then updates with the system (`apt upgrade`). Run it once on a clean server. For a pinned version use the [repository installation](https://docs.docker.com/engine/install/).
:::

## Install

```bash
mkdir -p /opt/gowave-docker && cd /opt/gowave-docker
curl -fsSLO https://raw.githubusercontent.com/aaaSaZaN/gowave/main/docker-compose.yml
curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/.env.docker.example -o .env

# Generate the secrets
sed -i "s/^APP_SECRET=.*/APP_SECRET=$(openssl rand -hex 32)/; s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -hex 24)/" .env

nano .env   # set PANEL_DOMAIN and SUB_PUBLIC_DOMAIN
docker compose up -d
```

The panel is published on `127.0.0.1:3000`. Next, set up a [reverse proxy](../reverse-proxy/overview/).

## How the compose file works

- **`gowave`** - the panel. The whole `.env` is passed to the container (`env_file`); the database connection and ports are set in the compose file and override `.env`.
- **`postgres`** - PostgreSQL 18 with the `postgres_data` volume mounted at `/var/lib/postgresql`. Its port is bound to `127.0.0.1` for backups and administration. Installs on PostgreSQL 17 are upgraded with a [separate guide](../../migration/postgres-18/).
- Both containers are on the `gowave-network` Docker network, the panel with the hostname `gowave`. Other containers on this server, such as the [subscription page](../subscription-page/), join it and reach the panel at `http://gowave:3000`.
- `APP_SECRET` and `POSTGRES_PASSWORD` are required: `docker compose` refuses to start without them.
- Metrics (`3001`) are reachable from `127.0.0.1` only; set `METRICS_USER` and `METRICS_PASS` to scrape them.

## Updates and CLI

Updates run on the server. The panel shows this command when a new version is out:

```bash
cd /opt/gowave-docker && docker compose pull && docker compose up -d
```

Panel CLI commands run inside the container:

```bash
docker compose exec gowave /app/gowave rescue --list-admins
```

Why there is no update button in Docker: see [Updating](../updating/).
