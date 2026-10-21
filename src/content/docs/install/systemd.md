---
title: Systemd и SQLite
description: Ручная установка GoWave одним бинарником с базой SQLite.
sidebar:
  order: 3
---

Самый лёгкий вариант: один бинарник, файл базы SQLite и служба systemd. Docker не нужен. Команды ниже выполняются от root.

## Файлы

```bash
mkdir -p /opt/gowave/frontend/dist && cd /opt/gowave
ARCH=$(uname -m | sed 's/x86_64/amd64/; s/aarch64/arm64/')
curl -fL -o gowave-server https://github.com/aaaSaZaN/gowave/releases/latest/download/gowave-linux-$ARCH
curl -fLO https://github.com/aaaSaZaN/gowave/releases/latest/download/gowave-frontend.tar.gz
chmod +x gowave-server && tar -xzf gowave-frontend.tar.gz -C frontend/dist
```

Контрольные суммы лежат в `SHA256SUMS` рядом с файлами релиза.

## Настройки

```bash
cat > .env <<ENV
APP_HOST=127.0.0.1
APP_PORT=3000
APP_SECRET=$(openssl rand -hex 32)
DB_DRIVER=sqlite
DATABASE_URL=gowave.db
PANEL_DOMAIN=panel.yourdomain.com
SUB_PUBLIC_DOMAIN=panel.yourdomain.com/api/sub
ENV
chmod 600 .env
```

Все переменные - в [справочнике](../../reference/environment/).

## Служба

Панель не запускается от root: служба работает от системного пользователя `gowave`. Создайте `/etc/systemd/system/gowave.service`:

```ini
[Unit]
Description=GoWave Panel
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=gowave
Group=gowave
WorkingDirectory=/opt/gowave
ExecStart=/opt/gowave/gowave-server
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

Пользователя и ограничения службы создаёт сам бинарник:

```bash
/opt/gowave/gowave-server service install /opt/gowave
ln -sfn /opt/gowave/gowave-server /usr/local/bin/gowave
systemctl enable --now gowave
```

Команда `service install`:

- создаёт системную группу и пользователя `gowave` без shell и домашнего каталога, если их ещё нет;
- отдаёт `/opt/gowave` этому пользователю, ставит каталогу права `0750`, а `.env` - `0600`;
- пишет `/etc/systemd/system/gowave.service.d/90-unprivileged.conf` и выполняет `systemctl daemon-reload`.

Сам `gowave.service` команда не трогает, поэтому ваши `Environment=` и другие настройки в нём сохраняются. Каталог должен быть отдельным: в путях `/opt`, `/usr/local`, `/home/...` и других общих каталогах команда откажется работать. В пути допустимы только латиница, цифры и `_ . / -`.

Вторая строка создаёт глобальную команду `gowave`. Установщик делает это сам, а служба от `gowave` записать в `/usr/local/bin` не может.

## Ограничения службы

`90-unprivileged.conf` переопределяет пользователя и запуск и закрывает службу от остальной системы:

```ini
[Service]
User=gowave
Group=gowave
WorkingDirectory=/opt/gowave
ExecStart=
ExecStart=/opt/gowave/gowave-server
DynamicUser=false
ProtectSystem=strict
ProtectHome=true
PrivateDevices=true
PrivateTmp=true
NoNewPrivileges=true
MemoryDenyWriteExecute=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true
UMask=0077
ReadWritePaths=/opt/gowave
RuntimeDirectory=gowave
RuntimeDirectoryMode=0700
RuntimeDirectoryPreserve=yes
Restart=always
CapabilityBoundingSet=
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=
AmbientCapabilities=CAP_NET_BIND_SERVICE
```

Писать служба может только в `/opt/gowave`, `/run/gowave` и свой отдельный `/tmp`. Остальная файловая система для неё только на чтение, а `/home` и `/root` не видны вовсе. Единственная оставшаяся привилегия - `CAP_NET_BIND_SERVICE`: она позволяет занять порт ниже 1024, если такой указан в `APP_PORT`.

`DynamicUser` выключен намеренно. Файл SQLite и бинарник должны принадлежать постоянному пользователю, иначе обновление из панели не сможет заменить бинарник. При обновлении панель подменяет файлы и завершается, а systemd поднимает её заново благодаря `Restart=always`.

Если панели нужно писать куда-то ещё, например в отдельный каталог для бэкапов, добавьте собственное переопределение. Файл `90-unprivileged.conf` перезаписывается при каждом `service install` и обновлении через установщик, поэтому правьте не его:

```bash
systemctl edit gowave
```

```ini
[Service]
ReadWritePaths=/srv/gowave-backups
```

Сам каталог тоже отдайте пользователю службы: `chown gowave:gowave /srv/gowave-backups`.

## Команды CLI

Запускайте их от `gowave` из каталога панели. Если запустить от root, SQLite может создать служебные файлы базы (`gowave.db-wal`, `gowave.db-shm`), которые служба потом не откроет:

```bash
cd /opt/gowave && sudo -u gowave gowave rescue
```

Все команды - в [справочнике CLI](../../reference/cli/).

## Старая служба от root

Если панель стояла с `User=root` (так ставили версии до v1.1.11), ничего делать не нужно. Новый бинарник при первом запуске под systemd сам выполнит `service install` для своего рабочего каталога и завершится, а systemd перезапустит его уже от `gowave`. Установщик при обновлении тоже заново применяет ограничения.

Дальше настройте [reverse proxy](../reverse-proxy/overview/).
