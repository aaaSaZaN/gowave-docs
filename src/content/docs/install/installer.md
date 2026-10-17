---
title: Установщик
description: Установка GoWave одной командой. SQLite или PostgreSQL в Docker, HTTPS через Caddy или Nginx.
sidebar:
  order: 1
---

Нужны сервер на Debian/Ubuntu или RHEL-семействе (`amd64` или `arm64`) и домен, A-запись которого указывает на IP сервера. Панель открывается только по домену через HTTPS, поэтому без домена установщик не продолжит.

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)"
```

## Что спросит установщик

1. **База данных.** SQLite - один файл, без Docker, обновление прямо из панели. Или PostgreSQL в Docker.
2. **Домен панели.** Установщик проверит, что он указывает на этот сервер.
3. **Reverse proxy.** Caddy (сертификат выпускается и продлевается сам) или Nginx с Certbot.

## Что он сделает сам

- скачает релиз и сверит контрольные суммы `SHA256SUMS`;
- сгенерирует `APP_SECRET`;
- создаст службу `gowave`;
- настроит reverse proxy с HTTPS;
- откроет порты 80 и 443 в `ufw` или `firewalld`.

Панель слушает только `127.0.0.1` и доступна по `https://<домен>`.

:::caution[Сразу откройте панель]
Первый, кто откроет панель, создаёт администратора. Зайдите в неё сразу после установки.
:::

## Переезд с другой панели

Если на сервере найдена **Remnawave** (`/opt/remnawave`) или **PasarGuard** (`/opt/pasarguard`, SQLite или PostgreSQL/TimescaleDB), установщик предложит перенести данные в GoWave - на SQLite или на PostgreSQL в Docker.

Старая панель останавливается и пропадает из автозагрузки, но её контейнеры и данные остаются на месте. Если перенос не удался, установщик включит её обратно. Подробнее - в разделе [Миграция](../../migration/remnawave/).

## Повторный запуск

Та же команда на сервере, где GoWave уже стоит, открывает меню: обновить, сменить домен и прокси, удалить (по желанию - с резервной копией базы).

Конкретную версию можно поставить так:

```bash
sudo GOWAVE_VERSION=v1.2.3 bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)"
```

Лог установки: `/var/log/gowave-install.log`.

## Ручная установка

Если установщик не подходит, панель ставится вручную:

- [Docker Compose и PostgreSQL](../docker/)
- [Systemd и SQLite](../systemd/)

В обоих случаях дальше нужен [reverse proxy](../reverse-proxy/overview/).
