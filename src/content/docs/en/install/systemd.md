---
title: Systemd and SQLite
description: Manual GoWave installation as a single binary with SQLite.
sidebar:
  order: 3
---

The lightest option: one binary, an SQLite file and a systemd service. No Docker. Run the commands below as root.

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

The panel does not run as root: the service runs as the `gowave` system user. Create `/etc/systemd/system/gowave.service`:

```ini
[Unit]
Description=GoWave Panel
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=gowave
Group=gowave
WorkingDirectory=/opt/gowave
ExecStart=/opt/gowave/gowave-server
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

The binary creates the user and the service restrictions itself:

```bash
/opt/gowave/gowave-server service install /opt/gowave
ln -sfn /opt/gowave/gowave-server /usr/local/bin/gowave
systemctl enable --now gowave
```

`service install`:

- creates the `gowave` system group and user, with no shell and no home directory, unless they exist;
- gives `/opt/gowave` to that user, with mode `0750` on the directory and `0600` on `.env`;
- writes `/etc/systemd/system/gowave.service.d/90-unprivileged.conf` and runs `systemctl daemon-reload`.

It never touches `gowave.service` itself, so your `Environment=` lines and other settings there stay. The directory has to be a dedicated one: the command refuses `/opt`, `/usr/local`, anything under `/home` and other shared paths. Only Latin letters, digits and `_ . / -` are allowed in the path.

The second line creates the global `gowave` command. The installer does this for you, and the service, running as `gowave`, cannot write to `/usr/local/bin`.

## Service restrictions

`90-unprivileged.conf` overrides the user and the start command and walls the service off from the rest of the system:

```ini
[Service]
User=gowave
Group=gowave
WorkingDirectory=/opt/gowave
ExecStart=
ExecStart=/opt/gowave/gowave-server
DynamicUser=false
ProtectSystem=strict
ProtectHome=true
PrivateDevices=true
PrivateTmp=true
NoNewPrivileges=true
MemoryDenyWriteExecute=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true
UMask=0077
ReadWritePaths=/opt/gowave
RuntimeDirectory=gowave
RuntimeDirectoryMode=0700
RuntimeDirectoryPreserve=yes
Restart=always
CapabilityBoundingSet=
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=
AmbientCapabilities=CAP_NET_BIND_SERVICE
```

The service can write only to `/opt/gowave`, `/run/gowave` and its own private `/tmp`. The rest of the file system is read-only for it, and `/home` and `/root` are not visible at all. The one privilege left is `CAP_NET_BIND_SERVICE`, so `APP_PORT` can be below 1024 if you set it that way.

`DynamicUser` is off on purpose: the SQLite files must belong to a stable user.

The panel code is owned by root. The service account cannot change `gowave-server` or `frontend/`, so a compromised panel cannot plant a binary that root later runs (the installer, `gowave rescue` via `sudo`). `/opt/gowave` is `root:gowave` with the sticky bit: the panel creates its database files there but cannot replace or remove root's files. `.env` is read-only for the panel.

Updates from the panel run in a separate root service. The panel leaves a request in `/run/gowave`, `gowave-update.path` starts `gowave-update.service`, which downloads the release, checks it against `SHA256SUMS`, installs it and restarts the panel.

If the panel needs to write somewhere else, say a separate backup directory, add an override of your own. `90-unprivileged.conf` is rewritten by every `service install` and every update through the installer, so do not edit it:

```bash
systemctl edit gowave
```

```ini
[Service]
ReadWritePaths=/srv/gowave-backups
```

Give the directory to the service user as well: `chown gowave:gowave /srv/gowave-backups`.

## CLI commands

Run them as `gowave` from the panel directory. If you run them as root, SQLite may create database side files (`gowave.db-wal`, `gowave.db-shm`) that the service then cannot open:

```bash
cd /opt/gowave && sudo -u gowave gowave rescue
```

All commands are in the [CLI reference](../../reference/cli/).

## Old root service

If the panel was installed with `User=root` (versions before v1.1.11 did that), there is nothing to do. On its first start under systemd the new binary runs `service install` for its working directory and exits, and systemd restarts it as `gowave`. The installer also reapplies the restrictions on every update.

Next, set up a [reverse proxy](../reverse-proxy/overview/).
