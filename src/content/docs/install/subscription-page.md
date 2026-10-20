---
title: Страница подписки
description: Развёртывание remnawave/subscription-page рядом с панелью или на отдельном сервере.
sidebar:
  order: 7
---

**Subscription Page** - страница для пользователей (`https://sub.yourdomain.com/<shortUuid>`): инструкции по подключению и QR-коды для приложений (Happ, sing-box, v2rayNG, Clash, Shadowrocket). Она также скрывает домен и IP панели от клиентов.

GoWave совместим с официальным образом `remnawave/subscription-page`.

## Подготовка

1. В панели откройте **Настройки**, затем **API-токены**.
2. Создайте токен с правами для страницы подписки и скопируйте его.

## Вариант 1: на сервере панели

1. В `.env` панели (`/opt/gowave-docker/.env` для Docker, `/opt/gowave/.env` для systemd) укажите домен страницы:

   ```ini
   SUB_PUBLIC_DOMAIN=sub.yourdomain.com
   ```

   И перезапустите панель: `docker compose up -d` (Docker) или `systemctl restart gowave` (systemd).

2. Создайте `/opt/gowave-sub/docker-compose.yml`. Страница работает в обычной сети Docker, а её порт опубликован только на `127.0.0.1`: снаружи до неё не достучаться в обход reverse proxy, и правило файрвола не нужно. Как страница обращается к панели, зависит от способа установки панели.

   **Панель в Docker.** Страница подключается к Docker-сети панели `gowave-network` и обращается к контейнеру панели напрямую по `http://gowave:3000`, мимо reverse proxy. Это та же схема, что у Remnawave с её `remnawave-network`:

   ```yaml
   services:
     gowave-subscription-page:
       image: remnawave/subscription-page:latest
       container_name: gowave-subpage
       hostname: gowave-subpage
       restart: always
       ports:
         - "127.0.0.1:3010:3010"
       environment:
         - APP_PORT=3010
         - REMNAWAVE_PANEL_URL=http://gowave:3000
         - REMNAWAVE_API_TOKEN=ВАШ_API_ТОКЕН
         - TRUST_PROXY=1
       networks:
         - gowave-network

   networks:
     gowave-network:
       external: true
   ```

   Сначала запустите панель: сеть `gowave-network` появляется после `docker compose up -d` в `/opt/gowave-docker`. Если `docker network ls` её не показывает, `docker-compose.yml` панели скачан до появления этой сети: скачайте [актуальный](https://raw.githubusercontent.com/aaaSaZaN/gowave/main/docker-compose.yml) (или перенесите из него секции `networks`) и снова выполните `docker compose up -d`.

   **Панель через systemd.** Панель слушает `127.0.0.1` хоста, а из контейнера этот адрес недоступен, поэтому страница обращается к панели через её домен:

   ```yaml
   services:
     gowave-subscription-page:
       image: remnawave/subscription-page:latest
       container_name: gowave-subpage
       restart: always
       ports:
         - "127.0.0.1:3010:3010"
       environment:
         - APP_PORT=3010
         - REMNAWAVE_PANEL_URL=https://panel.yourdomain.com
         - REMNAWAVE_API_TOKEN=ВАШ_API_ТОКЕН
         - TRUST_PROXY=1
   ```

   В `REMNAWAVE_PANEL_URL` указывается адрес **панели**. `APP_PORT` задаёт порт самой страницы подписки. Если меняете `APP_PORT`, поменяйте порт и в `ports`, и в reverse proxy.

   :::caution[Не используйте network_mode: host]
   В сети хоста страница подписки слушает порт из `APP_PORT` на всех адресах сервера, включая внешний: адрес для прослушивания в ней не настраивается, а `ports` в этом режиме не действует. Без правила файрвола порт открыт в интернет по HTTP, а с `TRUST_PROXY=1` клиент, подключившийся напрямую, может подменить свой IP через `X-Forwarded-For`.
   :::

3. Запустите: `cd /opt/gowave-sub && docker compose up -d`.

4. Направьте `sub.yourdomain.com` на `127.0.0.1:<APP_PORT>` в reverse proxy. Для Caddy с `APP_PORT=3010`:

   ```text
   sub.yourdomain.com {
       encode zstd gzip
       reverse_proxy 127.0.0.1:3010
   }
   ```

## Вариант 2: на отдельном сервере

Так клиенты не узнают IP сервера панели.

1. На сервере панели укажите `SUB_PUBLIC_DOMAIN=sub.yourdomain.com` в `.env` и перезапустите панель.
2. На отдельном сервере создайте `docker-compose.yml`:

   ```yaml
   services:
     gowave-subscription-page:
       image: remnawave/subscription-page:latest
       container_name: gowave-subpage
       restart: always
       ports:
         - "127.0.0.1:3010:3010"
       environment:
         - APP_PORT=3010
         - REMNAWAVE_PANEL_URL=https://panel.yourdomain.com
         - REMNAWAVE_API_TOKEN=ВАШ_API_ТОКЕН
         - TRUST_PROXY=1
   ```

3. Запустите `docker compose up -d` и направьте `sub.yourdomain.com` на `127.0.0.1:3010` в reverse proxy.
