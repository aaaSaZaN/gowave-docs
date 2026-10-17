---
title: Обновление
description: Как обновлять GoWave на systemd и в Docker.
sidebar:
  order: 5
---

Панель сама проверяет релизы на GitHub и показывает, что вышла новая версия. Pre-release (теги вида `v1.2.0-beta.1`) не предлагаются: их ставят вручную.

## Systemd и SQLite

Нажмите **Update panel** в окне версии в шапке панели. Панель скачает новый бинарник и веб-интерфейс, заменит их и перезапустится.

Или повторно запустите установщик - он откроет меню с пунктом обновления:

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)"
```

## Docker

В Docker кнопки нет - панель показывает команду, которую нужно выполнить на сервере:

```bash
cd /opt/gowave-docker && docker compose pull && docker compose up -d
```

Контейнер не может заменить собственный образ. Обновлять его должен кто-то снаружи, а для этого нужен доступ к Docker-сокету, то есть права root на хосте. Давать такой доступ веб-панели небезопасно: взлом панели превратился бы во взлом сервера. Поэтому обновление в Docker остаётся обычной командой.

## Версия

```bash
gowave --version
```

В Docker: `docker compose exec gowave /app/gowave --version`.
