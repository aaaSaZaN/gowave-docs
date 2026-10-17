---
title: Installer
description: Install GoWave with one command. SQLite or PostgreSQL in Docker, HTTPS via Caddy, Nginx or your own proxy.
sidebar:
  order: 1
---

You need a Debian/Ubuntu or RHEL-family server (`amd64` or `arm64`) and a domain whose A record points to the server. The panel is only served over HTTPS on that domain, so the installer will not continue without one. With your own proxy the domain may point elsewhere.

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)"
```

## What the installer asks

1. **Database.** SQLite: a single file, no Docker, updates from the panel. Or PostgreSQL in Docker.
2. **Reverse proxy.** Caddy (certificates are issued and renewed automatically), Nginx with Certbot, or your own proxy, see [below](#your-own-reverse-proxy).
3. **Panel domain.** For Caddy and Nginx the installer checks that the domain points to this server.

## What it does

- downloads the release and verifies `SHA256SUMS`;
- generates `APP_SECRET`;
- creates the `gowave` service;
- configures the reverse proxy with HTTPS and opens ports 80 and 443 in `ufw` or `firewalld` when Caddy or Nginx is chosen.

The panel listens on `127.0.0.1` only and is available at `https://<domain>`.

:::caution[Open the panel right away]
The first person to open the panel creates the administrator. Open it immediately after installing.
:::

## Your own reverse proxy

Pick "Не настраивать: свой reverse proxy" (do not configure, use your own) when the server already runs a proxy (Angie, Traefik, HAProxy, Caddy or Nginx in Docker), the proxy lives on another server, or the panel is reached through Cloudflare Tunnel. The installer then sets up only the panel and leaves ports 80 and 443, the proxy and the firewall alone. It also skips the DNS check.

At the end it prints the address to point the proxy at, usually `http://127.0.0.1:3000`. The proxy has to pass the `Host`, `X-Forwarded-For` and `X-Forwarded-Proto` headers, plus WebSocket (`Upgrade` and `Connection`) for the node SSH terminal. Ready-made configurations exist for [Caddy](../reverse-proxy/caddy/) and [Nginx](../reverse-proxy/nginx/).

:::note[Proxy in Docker]
The panel listens on the server's `127.0.0.1` only, so a proxy container on a regular Docker network cannot reach it. Run the proxy with `network_mode: host`.
:::

Until the proxy is set up, the panel opens only from the server itself, so nobody can create the administrator from outside. You can switch to Caddy or Nginx later with the "Настроить домен и HTTPS" (configure domain and HTTPS) menu item.

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
