---
title: Requirements
description: What a server needs to run GoWave.
sidebar:
  order: 1
---

- Linux on `amd64` or `arm64`: Debian, Ubuntu or a RHEL-family distribution.
- Root access.
- A domain with an A/AAAA record pointing to the server and a valid TLS certificate.
- Port 443/TCP open; port 80/TCP also open and free when using HTTP-01.
- A free local port for the panel. It is `127.0.0.1:3000` by default; if that port is taken, the installer picks the next free one.
- RAM for the panel: about 50-60 MB under load, and about 140 MB more for PostgreSQL.
- Disk space for the binary (about 28 MB), web interface, database and backups.
- For [Docker](../docker/): Docker Engine and the Docker Compose plugin; for [installation without Docker](../systemd/): systemd. The [installer](../installer/) installs Docker itself if you pick PostgreSQL.
