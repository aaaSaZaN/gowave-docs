---
title: Overview
description: Why the panel needs a reverse proxy and which one to pick.
sidebar:
  order: 1
---

The panel listens on `127.0.0.1:3000` only and is exposed through a reverse proxy with HTTPS. The installer sets this up; for a manual installation pick one of the two:

- [Caddy](../caddy/) is the simplest: certificates are issued and renewed automatically.
- [Nginx](../nginx/) fits if Nginx already runs on the server. Certificates come from Certbot.

:::tip[WebSocket]
The `Upgrade` and `Connection` headers are required for the node SSH terminal in the panel.
:::
