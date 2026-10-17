---
title: Installer
description: Install GoWave with one command. SQLite or PostgreSQL in Docker, HTTPS via Caddy or Nginx.
sidebar:
  order: 1
---

You need a Debian/Ubuntu or RHEL-family server (`amd64` or `arm64`) and a domain whose A record points to the server. The panel is only served over HTTPS on that domain, so the installer will not continue without one.

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)"
```

## What the installer asks

1. **Database.** SQLite: a single file, no Docker, updates from the panel. Or PostgreSQL in Docker.
2. **Panel domain.** The installer checks that it points to this server.
3. **Reverse proxy.** Caddy (certificates are issued and renewed automatically) or Nginx with Certbot.

## What it does

- downloads the release and verifies `SHA256SUMS`;
- generates `APP_SECRET`;
- creates the `gowave` service;
- configures the reverse proxy with HTTPS;
- opens ports 80 and 443 in `ufw` or `firewalld`.

The panel listens on `127.0.0.1` only and is available at `https://<domain>`.

:::caution[Open the panel right away]
The first person to open the panel creates the administrator. Open it immediately after installing.
:::

## Moving from another panel

If **Remnawave** (`/opt/remnawave`) or **PasarGuard** (`/opt/pasarguard`, SQLite or PostgreSQL/TimescaleDB) is found on the server, the installer offers to move its data to GoWave, on SQLite or on PostgreSQL in Docker.

The old panel is stopped and taken out of autostart, but its containers and data stay where they are. If the move fails, the installer brings it back. See [Migration](../../migration/remnawave/).

## Running it again

The same command on a server that already runs GoWave opens a menu: update, change domain and proxy, uninstall (optionally with a database backup).

To install a specific version:

```bash
sudo GOWAVE_VERSION=v1.2.3 bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)"
```

Install log: `/var/log/gowave-install.log`.

## Manual installation

If the installer does not fit your setup:

- [Docker Compose and PostgreSQL](../docker/)
- [Systemd and SQLite](../systemd/)

Both need a [reverse proxy](../reverse-proxy/overview/) afterwards.
