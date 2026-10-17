---
title: Docker Compose и PostgreSQL
description: Ручная установка GoWave в Docker вместе с PostgreSQL 18.
sidebar:
  order: 2
---

Образ панели публикуется в `ghcr.io/aaasazan/gowave` для `linux/amd64` и `linux/arm64`.

## Docker

Если Docker ещё не установлен, поставьте его официальным скриптом - он ставит Docker Engine и плагин `docker compose`:

```bash
curl -fsSL https://get.docker.com | sudo sh
```

:::note[Почему «не для production»]
Docker называет этот скрипт *convenience script*: он ставит последнюю версию без выбора, ничего не спрашивает и не предназначен для обновления уже установленного Docker. Для одного VPS с панелью это нормальный способ - скрипт подключает официальный репозиторий Docker, и дальше Docker обновляется вместе с системой (`apt upgrade`). Запускайте его один раз на чистом сервере. Если нужна закреплённая версия, используйте [установку из репозитория](https://docs.docker.com/engine/install/).
:::

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

## Как устроен compose

- **`gowave`** - панель. Весь `.env` передаётся в контейнер (`env_file`), а подключение к базе и порты задаются в самом compose и переопределяют `.env`.
- **`postgres`** - PostgreSQL 18 с томом `postgres_data`, смонтированным в `/var/lib/postgresql`. Порт открыт только на `127.0.0.1` для резервных копий и администрирования. Установки на PostgreSQL 17 обновляются по [отдельной инструкции](../../migration/postgres-18/).
- `APP_SECRET` и `POSTGRES_PASSWORD` обязательны: без них `docker compose` откажется запускаться.
- Метрики (`3001`) доступны только с `127.0.0.1`; задайте `METRICS_USER` и `METRICS_PASS`, чтобы их собирать.

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
