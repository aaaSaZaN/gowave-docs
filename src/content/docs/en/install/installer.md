---
title: Installer
description: Install GoWave with one command. SQLite or PostgreSQL in Docker, HTTPS via Caddy, Nginx or your own proxy.
sidebar:
  order: 2
---

You need a Debian/Ubuntu or RHEL-family server (`amd64` or `arm64`) and a domain whose A record points to the server. The panel is only served over HTTPS on that domain, so the installer will not continue without one. With your own proxy the domain may point elsewhere.

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)"
```

Run it in an SSH session: the installer asks questions and refuses to start without an interactive terminal. The exception is an update with [`--update`](#command-line-options). It also checks that it runs as root on a system with systemd and `apt` or `dnf`, and installs `curl`, `tar`, `openssl`, `ss` and `sha256sum` if any are missing.

## What the installer asks

1. **Language** of questions and messages: Russian or English.
2. **Migration.** If Remnawave or PasarGuard is found on the server, the installer offers to move its data, see [below](#moving-from-another-panel).
3. **Database.** SQLite: a single file, no Docker, updates from the panel. Or PostgreSQL in Docker. When migrating, you pick the database in the previous step.
4. **Update channel.** Stable for tested releases, Dev for a build of every commit to `main`, see [Updating](../updating/#stable-and-dev-channels).
5. **Reverse proxy.** Caddy (certificates are issued and renewed automatically), Nginx with Certbot, or your own proxy, see [below](#your-own-reverse-proxy).
6. **Panel domain.** For Caddy and Nginx the installer checks that the domain resolves and compares its A and AAAA records with the server's public IP. If they differ, for example behind the Cloudflare proxy, it asks whether to continue, since the certificate may not be issued.
7. **Dashboard path**, `/` by default, see [below](#dashboard-path).
8. **Local node.** Whether to install GoWave Node on the same server once the panel is ready, see [below](#local-node).

Next it looks at who holds ports 80 and 443. Only the chosen proxy already running on this server, or the old panel it is about to stop, may hold them. The panel itself gets the first free port from 3000 up.

Before installing, it shows a summary: the panel address, its local port, the database, the channel, the proxy and what happens to the old panel. Until you confirm, it installs nothing except the missing tools.

## What it does

1. Downloads the binary, the web interface and `SHA256SUMS` and verifies the checksums. On a mismatch the installation stops.
2. Writes `/opt/gowave/.env`: generates `APP_SECRET`, sets the domain, the dashboard path and the ports. The Prometheus metrics port is the first free one from 3001 up; metrics themselves are off (`METRICS_ENABLED=false`), and the file explains how to turn them on.
3. If you chose to migrate, copies the old panel's data and notification settings, then stops it.
4. Creates the `gowave` service, which runs as the `gowave` system user under systemd restrictions, and the `/usr/local/bin/gowave` command. See [Systemd and SQLite](../systemd/#service-restrictions) for the service details.
5. Starts the panel and waits for `/api/system/health` to answer.
6. For PostgreSQL, installs Docker from `get.docker.com` if needed and moves the panel to `/opt/gowave-docker` with [`gowave migrate to-docker`](../../migration/sqlite-to-docker/). So a PostgreSQL panel first starts on SQLite. Remnawave data goes straight into PostgreSQL, without a SQLite hop.
7. Sets up the proxy with HTTPS, opens ports 80 and 443 in `ufw` or `firewalld` and checks that the panel answers at `https://<domain>`.
8. Installs the local node if you said yes.

The panel listens on `127.0.0.1` only and is available at `https://<domain><dashboard path>`.

:::caution[Open the panel right away]
The first person to open the panel creates the administrator. Open it immediately after installing. After a move from Remnawave, log in with your existing administrator.
:::

### Caddy

Caddy comes from the official repository (Cloudsmith on Debian/Ubuntu, COPR on RHEL). The panel site goes to `/etc/caddy/gowave.caddy`. The installer replaces the stock `Caddyfile` from the package with an `import` line, and appends that line to a `Caddyfile` of your own. If Caddy rejects the result (for example, the domain is already defined there), the original `Caddyfile` is put back.

### Nginx

The installer adds `nginx` and `certbot`, from EPEL on RHEL. It first brings up a port 80 site, and Certbot gets the certificate through the `/var/www/gowave-acme` webroot. Then it writes the full `/etc/nginx/conf.d/gowave.conf`:

- redirect from HTTP to HTTPS, TLS 1.2 and 1.3, HTTP/2;
- WebSocket for the node SSH terminal with a one-hour timeout;
- response compression and requests up to 50 MB, enough to upload a backup;
- a block that drops the TLS handshake for any other name, so a scan by IP does not see the panel certificate. It is added with Nginx 1.19.4 or newer when you have no `default_server` of your own on 443.

The `/etc/letsencrypt/renewal-hooks/deploy/gowave-nginx.sh` hook reloads Nginx after a renewal. If the domain is already defined in another file under `/etc/nginx`, the installer stops and asks you to remove that `server` block. On SELinux systems it turns on `httpd_can_network_connect`, otherwise Nginx could not reach the panel.

## If the installation fails

If something fails before the panel first starts, the installer removes what it created: the service, the binary, the web interface, `.env`, the database and the `gowave` command. Anything else in `/opt/gowave` is left alone. If the old panel was already stopped, it is started again with its previous restart policy. Running the installer again starts from scratch.

Once the panel has started, the installer rolls nothing back. If the move to Docker fails, the panel keeps running on SQLite. If ports 80 and 443 got taken in the meantime, free them and run the installer again with "Set up domain and HTTPS". A failed node install leaves the panel alone; retry it from the menu.

## Files

| Path | Contents |
| :--- | :--- |
| `/opt/gowave` | Binary, web interface, `.env` and the `gowave.db` database |
| `/opt/gowave-docker` | `docker-compose.yml` and `.env` when PostgreSQL is chosen |
| `/etc/systemd/system/gowave.service` | Panel service |
| `/etc/systemd/system/gowave.service.d/90-unprivileged.conf` | Service user and restrictions |
| `/etc/systemd/system/gowave-update.path`, `gowave-update.service` | Root side of in-panel updates |
| `/usr/local/bin/gowave` | Link to the binary for the CLI |
| `/etc/caddy/gowave.caddy` | Caddy site |
| `/etc/nginx/conf.d/gowave.conf` | Nginx site |
| `/var/log/gowave-install.log` | Full installer log |

## Your own reverse proxy

Pick "Skip: I will use my own reverse proxy" when the server already runs a proxy (Angie, Traefik, HAProxy, Caddy or Nginx in Docker), the proxy lives on another server, or the panel is reached through Cloudflare Tunnel. The installer then sets up only the panel and leaves ports 80 and 443, the proxy and the firewall alone. It also skips the DNS check. The choice is saved in `.env` as `GOWAVE_PROXY=external`.

At the end it prints the address to point the proxy at, usually `http://127.0.0.1:3000`. The proxy has to forward the path unchanged and pass the `Host`, `X-Forwarded-For` and `X-Forwarded-Proto` headers, plus WebSocket (`Upgrade` and `Connection`) for the node SSH terminal. Ready-made configurations exist for [Caddy](../reverse-proxy/caddy/) and [Nginx](../reverse-proxy/nginx/).

:::note[Proxy in Docker]
The panel listens on the server's `127.0.0.1` only, so a proxy container on a regular Docker network cannot reach it. Run the proxy with `network_mode: host`.
:::

Until the proxy is set up, the panel opens only from the server itself, so nobody can create the administrator from outside. You can switch to Caddy or Nginx later with the "Set up domain and HTTPS" menu item.

## Dashboard path

The web interface can live under a path of its own instead of the domain root, for example `https://panel.example.com/private/panel/`. The installer asks for the path and writes it to `PANEL_BASE_PATH`. `panel`, `/panel` and `/panel/` mean the same thing. Use Latin letters, digits, `_` and `-`; nested paths work, and `/api` and `/metrics` are reserved.

The path moves only the dashboard. The API, subscriptions, WebSocket and metrics keep their addresses, so the path does not restrict API access. With a custom path, `/` answers 404.

The "Change dashboard path" menu item backs up `.env`, restarts the panel and checks that the dashboard opens at the new address. If the check fails, the previous `.env` comes back. Regular updates and the [move to Docker](../../migration/sqlite-to-docker/) keep the path.

## Local node

The installer can put [GoWave Node](../node/install/) on the same server: after the panel is installed (the last question) or with "Install or update the local node" from the menu. It takes the `SECRET_KEY` from the panel itself and runs the [node installer](../node/install/).

- For a new node it asks for a port, `2222` by default. An existing node keeps its port and key.
- The installer does not register the node in the panel or create a profile. Add the node yourself with the address and port it prints: `127.0.0.1` on systemd, the server's public IP in Docker, because the panel container cannot see the host's loopback.
- A failed node install does not stop the panel. Uninstalling the panel does not remove the node.

## Moving from another panel

If **Remnawave** (`/opt/remnawave`) or **PasarGuard** (`/opt/pasarguard`, SQLite or PostgreSQL/TimescaleDB) is found on the server, the installer offers to move its data to GoWave, on SQLite or on PostgreSQL in Docker. PasarGuard on MySQL or MariaDB cannot be moved. The installer does not import from [3x-ui](../../migration/3x-ui/); that is a separate command.

While copying, the installer stops only the old panel's app container; its database keeps running. After the move the old panel is stopped completely and taken out of autostart, but its containers and data stay where they are. If the move fails, the installer brings it back. See [Migration](../../migration/remnawave/).

## Running it again

The same command on a server that already runs GoWave opens a menu:

- "Update GoWave". It asks for the channel first; Enter keeps the current one. On systemd the installer downloads and verifies the new release, reapplies the service restrictions, restarts the panel and waits for it to answer. In Docker it sets the channel's image in `GOWAVE_IMAGE` and runs `docker compose pull` and `up`. A custom image (a local build or a mirror) is left alone. In older `docker-compose.yml` files it also binds the panel port to `127.0.0.1`. If no domain with HTTPS is set up yet, it offers to set one up.
- "Set up domain and HTTPS". Change the domain or switch between Caddy, Nginx and your own proxy. The installer removes the old proxy's config for the panel, updates `PANEL_DOMAIN` and `SUB_PUBLIC_DOMAIN` in `.env` and restarts the panel.
- "Change dashboard path", see [above](#dashboard-path).
- "Install or update the local node", see [above](#local-node).
- "Copy Telegram and webhook notifications from the old panel". Copies them from `/opt/remnawave/.env` into the GoWave `.env` and restarts the panel. `change_me` values are skipped. Telegram is turned on only with a bot token, and webhooks only with a valid `WEBHOOK_SECRET_HEADER`.
- "Uninstall GoWave". You have to type `yes`. Optionally the installer first saves `.env` and the database to `/root/gowave-backup-<date>`, using `pg_dump` for PostgreSQL. Then it removes the panel, its database, the PostgreSQL volume, the services, the `gowave` command and the Caddy or Nginx site. The Caddy and Nginx packages, Docker, certificates and the local node stay. If Caddy was set up only for GoWave, it is disabled.

## Command-line options

Pass options after `_` or as environment variables, for example from Ansible:

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)" _ --dev
```

| Option | Variable | What it does |
| :--- | :--- | :--- |
| `--stable`, `--dev`, `--channel stable\|dev` | `GOWAVE_CHANNEL` | Update channel without asking |
| `--version v1.2.3` | `GOWAVE_VERSION` | Pin a stable release. `dev` selects the dev channel |
| `--update` | `GOWAVE_ACTION=update` | Update an existing install with no prompts and no terminal |
| `--lang ru\|en` | `GOWAVE_LANG` | Message language without asking |

`--update` keeps the installed channel unless you give one, so it works from cron and Ansible:

```bash
curl -fsSL -o /tmp/gowave-install.sh https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh
sudo bash /tmp/gowave-install.sh --update --lang en
```

A fresh install still needs a terminal, because it asks about the domain, the proxy and the database. Ready-made playbooks live in [gowave-ansible](https://github.com/aaaSaZaN/gowave-ansible).

## Manual installation

If the installer does not fit your setup:

- [Docker Compose and PostgreSQL](../docker/)
- [Systemd and SQLite](../systemd/)

Both need a [reverse proxy](../reverse-proxy/overview/) afterwards.
