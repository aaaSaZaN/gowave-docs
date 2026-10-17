---
title: Systemd and SQLite
description: Manual GoWave installation as a single binary with SQLite.
sidebar:
  order: 3
---

The lightest option: one binary, an SQLite file and a systemd service. No Docker.

## Files

```bash
mkdir -p /opt/gowave/frontend/dist && cd /opt/gowave
ARCH=$(uname -m | sed 's/x86_64/amd64/; s/aarch64/arm64/')
curl -fL -o gowave-server https://github.com/aaaSaZaN/gowave/releases/latest/download/gowave-linux-$ARCH
curl -fLO https://github.com/aaaSaZaN/gowave/releases/latest/download/gowave-frontend.tar.gz
chmod +x gowave-server && tar -xzf gowave-frontend.tar.gz -C frontend/dist
```

Checksums are in `SHA256SUMS` next to the release files.

## Settings

```bash
cat > .env <<ENV
APP_HOST=127.0.0.1
APP_PORT=3000
APP_SECRET=$(openssl rand -hex 32)
DB_DRIVER=sqlite
DATABASE_URL=gowave.db
PANEL_DOMAIN=panel.yourdomain.com
SUB_PUBLIC_DOMAIN=panel.yourdomain.com/api/sub
ENV
chmod 600 .env
```

All variables are listed in the [reference](../../reference/environment/).

## Service

`/etc/systemd/system/gowave.service`:

```ini
[Unit]
Description=GoWave Panel
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/gowave
ExecStart=/opt/gowave/gowave-server
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload && systemctl enable --now gowave
```

When started as root for the first time, the binary registers the global `gowave` command (`/usr/local/bin/gowave`).

Next, set up a [reverse proxy](../reverse-proxy/overview/).
