---
title: Overview
description: Why the panel needs a reverse proxy and which one to pick.
sidebar:
  order: 1
---

The panel listens on `127.0.0.1:3000` only and is exposed through a reverse proxy with HTTPS. The installer sets this up; for a manual installation there are ready-made configurations:

- [Caddy](../caddy/) is the simplest: certificates are issued and renewed automatically.
- [Nginx](../nginx/) fits if Nginx already runs on the server. Certificates come from Certbot.
- [Panel and node on one server](../ssl-preread/): Nginx shares port 443 between the panel and Xray with REALITY.

Any other proxy works too (Angie, Traefik, HAProxy, Cloudflare Tunnel). It has to:

- forward requests to `http://127.0.0.1:3000` with the path unchanged;
- pass the `Host`, `X-Forwarded-For` and `X-Forwarded-Proto` headers;
- let WebSocket through (see below);
- accept uploads up to 50 MB if you restore backups through the panel.

If the proxy runs in Docker, start it with `network_mode: host`: the panel listens on the host's `127.0.0.1`, which a regular Docker network cannot see.

A [dashboard path](../../installer/#dashboard-path) (`PANEL_BASE_PATH`) needs no extra proxy setup: proxy the whole domain as is. The path moves only the web interface; the API and subscriptions stay at `/api/...`.

:::tip[WebSocket]
The `Upgrade` and `Connection` headers are required for the node SSH terminal in the panel.
:::
