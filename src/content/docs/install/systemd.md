---
title: Systemd и SQLite
description: Ручная установка GoWave одним бинарником с базой SQLite.
sidebar:
  order: 3
---

Самый лёгкий вариант: один бинарник, файл базы SQLite и служба systemd. Docker не нужен.

## Файлы

```bash
mkdir -p /opt/gowave/frontend/dist && cd /opt/gowave
ARCH=$(uname -m | sed 's/x86_64/amd64/; s/aarch64/arm64/')
curl -fL -o gowave-server https://github.com/aaaSaZaN/gowave/releases/latest/download/gowave-linux-$ARCH
curl -fLO https://github.com/aaaSaZaN/gowave/releases/latest/download/gowave-frontend.tar.gz
chmod +x gowave-server && tar -xzf gowave-frontend.tar.gz -C frontend/dist
```

Контрольные суммы лежат в `SHA256SUMS` рядом с файлами релиза.

## Настройки

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

Все переменные - в [справочнике](../../reference/environment/).

## Служба

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

При первом запуске от root бинарник регистрирует глобальную команду `gowave` (`/usr/local/bin/gowave`).

Дальше настройте [reverse proxy](../reverse-proxy/overview/).
