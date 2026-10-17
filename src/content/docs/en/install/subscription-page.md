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

2. Create `/opt/gowave-sub/docker-compose.yml`. The page runs on the host network and reaches the panel directly at `127.0.0.1:3000`, bypassing the reverse proxy. This works the same for Docker and systemd installations: in both the panel listens on the host's `127.0.0.1:3000`.

   ```yaml
   services:
     gowave-subscription-page:
       image: remnawave/subscription-page:latest
       container_name: gowave-subpage
       restart: always
       network_mode: host
       environment:
         - APP_PORT=3010
         - REMNAWAVE_PANEL_URL=http://127.0.0.1:3000
         - REMNAWAVE_API_TOKEN=YOUR_API_TOKEN
         - TRUST_PROXY=1
   ```

   `REMNAWAVE_PANEL_URL` is the address of the **panel**; `APP_PORT` is the subscription page's own port.

   :::caution[Close the APP_PORT port]
   On the host network the subscription page listens on its `APP_PORT` on every address of the server, not only `127.0.0.1`: it has no listen address setting, and `ports` bindings do not apply in this mode. Only 80 and 443 should be open to the outside. With `ufw` (use your `APP_PORT`; the example uses `3010`):

   ```bash
   ufw deny 3010/tcp
   ```

   Check from another machine: `curl http://<server IP>:<APP_PORT>` must not answer. If you change `APP_PORT`, close the new port and update the reverse proxy address.
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
