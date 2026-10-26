---
title: Docker Compose и PostgreSQL
description: Ручная установка GoWave в Docker вместе с PostgreSQL 18.
sidebar:
  order: 2
---

Образ панели публикуется в `ghcr.io/aaasazan/gowave` для `linux/amd64` и `linux/arm64`.

## Docker

Выполняйте команды ниже от root. Если уже установлены неофициальные пакеты Docker или конфликтующие `containerd`/`runc`, удалите конфликтующие пакеты по инструкции для своего дистрибутива.

### Debian / Ubuntu

Добавьте ключ подписи и APT-репозиторий Docker, затем установите Engine и плагин Compose. Команды используют `ID` и кодовое имя выпуска из `/etc/os-release` и предназначены для Debian и Ubuntu:

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

Официальные инструкции: [Debian](https://docs.docker.com/engine/install/debian/), [Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

### RHEL-like

Для RHEL 8/9/10 добавьте DNF-репозиторий Docker и установите пакеты:

```bash
dnf install dnf-plugins-core
dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Для CentOS Stream и совместимых дистрибутивов, например AlmaLinux и Rocky Linux, замените `linux/rhel/docker-ce.repo` на `linux/centos/docker-ce.repo` в команде добавления репозитория. Официальные инструкции: [RHEL](https://docs.docker.com/engine/install/rhel/), [CentOS](https://docs.docker.com/engine/install/centos/).

### Запуск и проверка

После установки любым из способов:

```bash
systemctl enable --now docker
docker run --rm hello-world
docker compose version
```

## Установка

```bash
mkdir -p /opt/gowave-docker && cd /opt/gowave-docker
curl -fsSLO https://raw.githubusercontent.com/aaaSaZaN/gowave/main/docker-compose.yml
curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/.env.docker.example -o .env

# Секреты генерируются автоматически
sed -i "s/^APP_SECRET=.*/APP_SECRET=$(openssl rand -hex 32)/; s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -hex 24)/" .env

nano .env   # укажите PANEL_DOMAIN и SUB_PUBLIC_DOMAIN
docker compose up -d
```

Панель публикуется на `127.0.0.1:3000`. Дальше настройте [reverse proxy](../reverse-proxy/overview/).

## Обновление и CLI

Обновление выполняется на сервере - панель покажет эту команду, когда выйдет новая версия:

```bash
cd /opt/gowave-docker && docker compose pull && docker compose up -d
```

CLI-команды панели запускаются внутри контейнера:

```bash
docker compose exec gowave /app/gowave rescue --list-admins
```

Почему нет кнопки обновления в Docker - в разделе [Обновление](../updating/).
