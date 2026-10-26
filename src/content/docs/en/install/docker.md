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

nano .env   # set PANEL_DOMAIN and SUB_PUBLIC_DOMAIN
docker compose up -d
```

The panel is published on `127.0.0.1:3000`. Next, set up a [reverse proxy](../reverse-proxy/overview/).

## Updates and CLI

Updates run on the server. The panel shows this command when a new version is out:

```bash
cd /opt/gowave-docker && docker compose pull && docker compose up -d
```

Panel CLI commands run inside the container:

```bash
docker compose exec gowave /app/gowave rescue --list-admins
```

Why there is no update button in Docker: see [Updating](../updating/).
