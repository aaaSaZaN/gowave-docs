---
title: Docker Compose and PostgreSQL
description: Manual GoWave installation in Docker with PostgreSQL 18.
sidebar:
  order: 2
---

The panel image is published as `ghcr.io/aaasazan/gowave` for `linux/amd64` and `linux/arm64`.

## Docker

Run the commands below as root. If unofficial Docker packages or a conflicting `containerd`/`runc` are installed, remove the conflicting packages as described in the instructions for your distribution.

### Debian / Ubuntu

Add Docker's signing key and APT repository, then install Engine and the Compose plugin. The commands use `ID` and the release codename from `/etc/os-release` and are intended for Debian and Ubuntu:

```bash
apt update
apt install ca-certificates curl
install -m 0755 -d /etc/apt/keyrings

. /etc/os-release
curl -fsSL "https://download.docker.com/linux/${ID}/gpg" -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

cat > /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/${ID}
Suites: ${UBUNTU_CODENAME:-$VERSION_CODENAME}
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

apt update
apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Official instructions: [Debian](https://docs.docker.com/engine/install/debian/), [Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

### RHEL-like

For RHEL 8/9/10, add Docker's DNF repository and install the packages:

```bash
dnf install dnf-plugins-core
dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

For CentOS Stream and compatible distributions such as AlmaLinux and Rocky Linux, replace `linux/rhel/docker-ce.repo` with `linux/centos/docker-ce.repo` in the repository command. Official instructions: [RHEL](https://docs.docker.com/engine/install/rhel/), [CentOS](https://docs.docker.com/engine/install/centos/).

### Start and verify

For either package manager:

```bash
systemctl enable --now docker
docker run --rm hello-world
docker compose version
```

## Install

```bash
mkdir -p /opt/gowave-docker && cd /opt/gowave-docker
curl -fsSLO https://raw.githubusercontent.com/aaaSaZaN/gowave/main/docker-compose.yml
curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/.env.docker.example -o .env

# Generate the secrets
sed -i "s/^APP_SECRET=.*/APP_SECRET=$(openssl rand -hex 32)/; s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -hex 24)/" .env

nano .env   # set PANEL_DOMAIN and SUB_PUBLIC_DOMAIN, and PANEL_BASE_PATH if you want one
docker compose up -d
```

The panel is published on `127.0.0.1:3000`. Next, set up a [reverse proxy](../reverse-proxy/overview/).

Every variable in `.env` reaches the panel container. The compose file sets the ports, `APP_SECRET` and the database connection itself: inside the container the panel always listens on `0.0.0.0:3000` and talks to the project's PostgreSQL. The other settings are in the [reference](../../reference/environment/).

## What is inside

The project has two containers on the `gowave-network` network:

| Container | Image | Host ports |
| :--- | :--- | :--- |
| `gowave` | `ghcr.io/aaasazan/gowave:latest` (or whatever `GOWAVE_IMAGE` names) | `127.0.0.1:3000` for the panel, `127.0.0.1:3001` for metrics |
| `gowave-postgres` | `postgres:18` | `127.0.0.1:5432` for migrations, backups and administration |

The panel image is built on Alpine and holds only the `/app/gowave` binary and the web interface. The panel container is locked down more than Docker's defaults:

- it runs as the unprivileged UID/GID `10001`;
- all capabilities are dropped (`cap_drop: ALL`) and privilege escalation is off (`no-new-privileges`);
- the root filesystem is read-only. Only `/tmp` is writable: a 128 MB tmpfs that cannot run files.

Because of the last point, a backup larger than 128 MB cannot be restored through the panel in Docker: the upload goes to a temporary file in `/tmp`. Mount your own files, such as [`notifications-config.yml`](../../features/notifications/#per-event-settings), as read-only volumes.

Docker checks the panel's health with a request to `/api/system/health`, and PostgreSQL with `pg_isready`. The panel starts only once the database is ready.

Logs of both containers are rotated: up to 5 files of 20 MB per container. Without that, Docker keeps logs without a limit. See [Logs](../../reference/logs/) for how to read them.

`.env.docker.example` has no `METRICS_ENABLED`, so the metrics port is open in Docker, though only on `127.0.0.1`. Until `METRICS_USER` and `METRICS_PASS` are set, `/metrics` answers 401.

## CLI

One command opens the rescue menu:

```bash
docker exec -it gowave cli
```

`rescue` does the same. Flags are passed through, and they do not need `-it`:

```bash
docker exec gowave cli --list-admins
```

Run other commands through the binary itself: `docker exec -it gowave /app/gowave <command>`. All commands are in the [CLI reference](../../reference/cli/).

## Updates

Updates run on the server. The panel shows this command when a new version is out:

```bash
cd /opt/gowave-docker && docker compose pull && docker compose up -d
```

How to switch to the dev channel, and why there is no update button in Docker: see [Updating](../updating/#docker).
