---
title: Updating
description: Updating GoWave on systemd and in Docker.
sidebar:
  order: 5
---

The panel checks GitHub releases and shows when a new version is out. Pre-releases (tags like `v1.2.0-beta.1`) are not offered; install them manually.

## Systemd and SQLite

Click **Update panel** in the version window in the panel header. The panel downloads the new binary and web interface, replaces them and restarts.

Or run the installer again. Its menu has an update option:

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)"
```

## Docker

There is no button in Docker. The panel shows the command to run on the server instead:

```bash
cd /opt/gowave-docker && docker compose pull && docker compose up -d
```

A container cannot replace its own image. Something outside has to do it, and that requires the Docker socket, which means root on the host. Giving that to a web panel would turn a panel compromise into a server compromise, so Docker updates stay a regular command.

## Version

```bash
gowave --version
```

In Docker: `docker compose exec gowave /app/gowave --version`.
