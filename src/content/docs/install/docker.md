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

nano .env   # укажите PANEL_DOMAIN и SUB_PUBLIC_DOMAIN, при желании PANEL_BASE_PATH
docker compose up -d
```

Панель публикуется на `127.0.0.1:3000`. Дальше настройте [reverse proxy](../reverse-proxy/overview/).

Каждая переменная из `.env` попадает в контейнер панели. Порты, `APP_SECRET` и подключение к базе compose-файл задаёт сам: внутри контейнера панель всегда слушает `0.0.0.0:3000` и ходит в PostgreSQL проекта. Остальные настройки описаны в [справочнике](../../reference/environment/).

## Что внутри

Проект состоит из двух контейнеров в сети `gowave-network`:

| Контейнер | Образ | Порты на хосте |
| :--- | :--- | :--- |
| `gowave` | `ghcr.io/aaasazan/gowave:latest` (или другой из `GOWAVE_IMAGE`) | `127.0.0.1:3000` - панель, `127.0.0.1:3001` - метрики |
| `gowave-postgres` | `postgres:18` | `127.0.0.1:5432` - для миграций, бэкапов и администрирования |

Образ панели собран на Alpine, внутри только бинарник `/app/gowave` и веб-интерфейс. Контейнер панели закрыт сильнее, чем по умолчанию:

- работает от непривилегированного пользователя с UID/GID `10001`;
- все capabilities сброшены (`cap_drop: ALL`), повышение прав запрещено (`no-new-privileges`);
- корневая файловая система только для чтения. Писать можно лишь в `/tmp`: это tmpfs на 128 МБ без права запуска файлов.

Из-за последнего пункта бэкап больше 128 МБ через панель в Docker не восстановится: загрузка складывается во временный файл в `/tmp`. Свои файлы, например [`notifications-config.yml`](../../features/notifications/#тонкая-настройка-событий), монтируйте томом только для чтения.

Здоровье панели Docker проверяет запросом к `/api/system/health`, PostgreSQL - через `pg_isready`. Панель стартует только после того, как база готова.

Логи обоих контейнеров ротируются: до 5 файлов по 20 МБ на контейнер. Без этого Docker хранит логи без ограничений. Как их читать, написано на странице [Журнал](../../reference/logs/).

В `.env.docker.example` нет `METRICS_ENABLED`, поэтому порт метрик в Docker открыт, но только на `127.0.0.1`. Пока не заданы `METRICS_USER` и `METRICS_PASS`, `/metrics` отвечает 401.

## CLI

Меню восстановления открывается одной командой:

```bash
docker exec -it gowave cli
```

`rescue` - то же самое. Флаги передаются как есть, `-it` для них не нужен:

```bash
docker exec gowave cli --list-admins
```

Остальные команды запускайте через сам бинарник: `docker exec -it gowave /app/gowave <команда>`. Все команды - в [справочнике CLI](../../reference/cli/).

## Обновление

Обновление выполняется на сервере - панель покажет эту команду, когда выйдет новая версия:

```bash
cd /opt/gowave-docker && docker compose pull && docker compose up -d
```

Как перейти на канал dev и почему в Docker нет кнопки обновления - в разделе [Обновление](../updating/#docker).
