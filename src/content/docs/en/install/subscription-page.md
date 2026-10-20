---
title: Subscription page
description: Deploying remnawave/subscription-page next to the panel or on a separate server.
sidebar:
  order: 7
---

The **Subscription Page** is the page your users open (`https://sub.yourdomain.com/<shortUuid>`): connection instructions and QR codes for apps (Happ, sing-box, v2rayNG, Clash, Shadowrocket). It also hides the panel's domain and IP from clients.

GoWave works with the official `remnawave/subscription-page` image.

## Preparation

1. In the panel, open **Settings**, then **API tokens**.
2. Create a token with subscription page permissions and copy it.

## Option 1: on the panel server

1. Set the page domain in the panel `.env` (`/opt/gowave-docker/.env` for Docker, `/opt/gowave/.env` for systemd):

   ```ini
   SUB_PUBLIC_DOMAIN=sub.yourdomain.com
   ```

   Then restart the panel: `docker compose up -d` (Docker) or `systemctl restart gowave` (systemd).

2. Create `/opt/gowave-sub/docker-compose.yml`. The page runs on a regular Docker network and its port is published on `127.0.0.1` only, so the outside world cannot reach it past the reverse proxy and no firewall rule is needed. How the page reaches the panel depends on how the panel is installed.

   **Panel in Docker.** The page joins the panel's Docker network `gowave-network` and talks to the panel container directly at `http://gowave:3000`, bypassing the reverse proxy. This is the same scheme as Remnawave with its `remnawave-network`:

   ```yaml
   services:
     gowave-subscription-page:
       image: remnawave/subscription-page:latest
       container_name: gowave-subpage
       hostname: gowave-subpage
       restart: always
       ports:
         - "127.0.0.1:3010:3010"
       environment:
         - APP_PORT=3010
         - REMNAWAVE_PANEL_URL=http://gowave:3000
         - REMNAWAVE_API_TOKEN=YOUR_API_TOKEN
         - TRUST_PROXY=1
       networks:
         - gowave-network

   networks:
     gowave-network:
       external: true
   ```

   Start the panel first: the `gowave-network` network appears after `docker compose up -d` in `/opt/gowave-docker`. If `docker network ls` does not list it, the panel's `docker-compose.yml` predates the network: download the [current one](https://raw.githubusercontent.com/aaaSaZaN/gowave/main/docker-compose.yml) (or copy its `networks` sections) and run `docker compose up -d` again.

   **Panel under systemd.** The panel listens on the host's `127.0.0.1`, which a container cannot reach, so the page goes through the panel domain:

   ```yaml
   services:
     gowave-subscription-page:
       image: remnawave/subscription-page:latest
       container_name: gowave-subpage
       restart: always
       ports:
         - "127.0.0.1:3010:3010"
       environment:
         - APP_PORT=3010
         - REMNAWAVE_PANEL_URL=https://panel.yourdomain.com
         - REMNAWAVE_API_TOKEN=YOUR_API_TOKEN
         - TRUST_PROXY=1
   ```

   `REMNAWAVE_PANEL_URL` is the address of the **panel**; `APP_PORT` is the subscription page's own port. If you change `APP_PORT`, change the port in `ports` and in the reverse proxy as well.

   :::caution[Do not use network_mode: host]
   On the host network the page listens on its `APP_PORT` on every address of the server, including the public one: it has no listen address setting, and `ports` does not apply in that mode. Without a firewall rule the port is open to the internet over plain HTTP, and with `TRUST_PROXY=1` a client connecting directly can spoof its IP through `X-Forwarded-For`.
   :::

3. Start it: `cd /opt/gowave-sub && docker compose up -d`.

4. Point `sub.yourdomain.com` to `127.0.0.1:<APP_PORT>` in the reverse proxy. For Caddy with `APP_PORT=3010`:

   ```text
   sub.yourdomain.com {
       encode zstd gzip
       reverse_proxy 127.0.0.1:3010
   }
   ```

## Option 2: on a separate server

This way clients never learn the panel server's IP.

1. On the panel server set `SUB_PUBLIC_DOMAIN=sub.yourdomain.com` in `.env` and restart the panel.
2. On the separate server create `docker-compose.yml`:

   ```yaml
   services:
     gowave-subscription-page:
       image: remnawave/subscription-page:latest
       container_name: gowave-subpage
       restart: always
       ports:
         - "127.0.0.1:3010:3010"
       environment:
         - APP_PORT=3010
         - REMNAWAVE_PANEL_URL=https://panel.yourdomain.com
         - REMNAWAVE_API_TOKEN=YOUR_API_TOKEN
         - TRUST_PROXY=1
   ```

3. Run `docker compose up -d` and point `sub.yourdomain.com` at `127.0.0.1:3010` in the reverse proxy.
