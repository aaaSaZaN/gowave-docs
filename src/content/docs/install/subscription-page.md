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

2. Создайте `/opt/gowave-sub/docker-compose.yml`. Страница работает в сети хоста и обращается к панели напрямую по `127.0.0.1:3000`, мимо reverse proxy. Это одинаково работает для установки через Docker и через systemd: в обоих случаях панель слушает `127.0.0.1:3000` на хосте.

   ```yaml
   services:
     gowave-subscription-page:
       image: remnawave/subscription-page:latest
       container_name: gowave-subpage
       restart: always
       network_mode: host
       environment:
         - APP_PORT=3010
         - REMNAWAVE_PANEL_URL=http://127.0.0.1:3000
         - REMNAWAVE_API_TOKEN=ВАШ_API_ТОКЕН
         - TRUST_PROXY=1
   ```

   В `REMNAWAVE_PANEL_URL` указывается адрес **панели**. `APP_PORT` задаёт порт самой страницы подписки.

   :::caution[Закройте порт из APP_PORT]
   В сети хоста страница подписки слушает порт из `APP_PORT` на всех адресах сервера, включая внешний. Адрес для прослушивания в ней не настраивается, а привязка из `ports` в этом режиме не действует. Наружу должны быть открыты только 80 и 443. С `ufw` (подставьте свой `APP_PORT`, в примере это `3010`):

   ```bash
   ufw deny 3010/tcp
   ```

   Проверить можно с другого компьютера: `curl http://<IP сервера>:<APP_PORT>` не должен отвечать. Если меняете `APP_PORT`, закройте новый порт и поменяйте адрес в reverse proxy.
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
