---
title: Установка
description: Установка Go-ноды одной командой.
sidebar:
  order: 1
---

Go-нода ([remnanode-go](https://github.com/aaaSaZaN/remnanode-go)) управляет ядром Xray на сервере, через который идёт трафик пользователей. Это реализация ноды Remnawave на Go: она совместима с Remnawave Node 3.4.2 и подключается как к GoWave, так и к оригинальной панели Remnawave. Xray работает отдельным процессом, Node.js и Docker не нужны.

## Требования

- Linux. Архитектуры: `amd64`, `386`, `arm64`, `armv7`, `armv6`, `armv5`, `riscv64`, `mips`, `mipsle`, `mips64`, `mips64le`. Серверные проверки проходят на `amd64` и `arm64`, остальные сборки для роутеров не сертифицированы.
- Система запуска: systemd, OpenRC (Alpine) или procd (OpenWrt).
- `curl` или `wget` и любой из `sha256sum`, `shasum`, `openssl`.
- Доступ root.
- Отдельный сервер: на одном сервере с панелью нода не поддерживается, см. [требования к панели](../../requirements/).
- Для фильтров трафика в плагинах нужны `nft`, `ss` (iproute2) и право `CAP_NET_ADMIN`.

## Установка

1. В панели добавьте ноду и скопируйте её `SECRET_KEY` из настроек ноды.
2. На сервере ноды выполните:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/remnanode-go/main/install.sh | sudo sh
   ```

   Без `curl` подойдёт `wget -qO- <тот же адрес> | sudo sh`.

3. Установщик спросит `SECRET_KEY` и `NODE_PORT` (по умолчанию `3000`). Порт должен совпадать с портом ноды в панели.

Без вопросов, например из скрипта:

```bash
curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/remnanode-go/main/install.sh | sudo SECRET_KEY=... NODE_PORT=2222 sh
```

## Что делает установщик

- определяет архитектуру и систему запуска (переопределяется через `REMNANODE_INIT=systemd|openrc|procd`);
- скачивает ноду и сверяет контрольные суммы, а также индекс ASN для плагинов и `geocheck` (на `amd64` и `arm64`);
- ставит последнюю стабильную версию Xray командой `remnanode core install` и проверяет её контрольную сумму;
- создаёт службу и запускает ноду.

Всё скачивается и проверяется до того, как установщик что-то меняет на сервере. При ошибке он возвращает прежнее состояние.

После запуска нода ждёт, пока панель пришлёт ей конфигурацию. Если панель ещё не настроила ноду, установщик сообщит об этом, а нода останется установленной: проверьте, что она добавлена в панели, и выполните `remnanode status`.

## Та же команда для обновления и переезда

Повторный запуск на сервере с Go-нодой обновляет её, сохраняя `.env`. На сервере с Docker-контейнером `remnawave/node` команда переводит его на Go-ноду, см. [переход с Docker-ноды](../../../migration/docker-node/).

Конкретную версию ставят так:

```bash
curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/remnanode-go/main/install.sh | sudo REMNANODE_VERSION=v1.0.6 sh
```

Если такого тега нет, установщик завершится с ошибкой, не трогая службы.

## Ручная установка

Бинарники `remnanode-linux-<архитектура>` и `checksums.txt` лежат в [релизах remnanode-go](https://github.com/aaaSaZaN/remnanode-go/releases). Положите бинарник в `/opt/remnanode`, создайте `.env` по [описанию настроек](../configuration/) и службу systemd:

```ini
[Unit]
Description=Remnanode (Go)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/remnanode
ExecStart=/opt/remnanode/remnanode
RuntimeDirectory=remnanode
RuntimeDirectoryMode=0700
UMask=0077
Restart=on-failure
RestartSec=3
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

Затем установите ядро: `/opt/remnanode/remnanode core install -y`.
