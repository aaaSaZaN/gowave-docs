---
title: С SQLite на Docker
description: Перевод установки GoWave с SQLite в Docker с PostgreSQL одной командой.
sidebar:
  order: 3
---

Перевод установки с SQLite в Docker одной командой. Нужен Docker с плагином compose; запускать от root на сервере панели:

```bash
gowave migrate to-docker
```

Команда:

1. находит текущую установку (`/opt/gowave`) и её `.env`, проверяет SQLite на битые ссылки между таблицами - до любых изменений;
2. создаёт `/opt/gowave-docker` с `docker-compose.yml` и `.env`: переносит **тот же** `APP_SECRET` и все настройки, генерирует пароль PostgreSQL;
3. скачивает образы, запускает PostgreSQL, останавливает `gowave.service` и копирует данные;
4. запускает панель в Docker на том же порту и ждёт, пока она ответит;
5. отключает `gowave.service`; команда `gowave` дальше выполняется внутри контейнера.

:::caution[APP_SECRET]
`APP_SECRET` участвует в хешах паролей администраторов, API-токенах и шифровании SSH-данных нод. Команда переносит его сама; при ручном переезде используйте тот же секрет, иначе вы не войдёте в панель.
:::

Если любой шаг не удался, Docker-проект удаляется, а старая панель запускается обратно. Файл SQLite не меняется, поэтому откатиться можно и позже:

```bash
cd /opt/gowave-docker && docker compose down
ln -sf /opt/gowave/gowave-server /usr/local/bin/gowave
systemctl enable --now gowave
```

Флаги: `--dir <путь>` (папка проекта), `--image <образ>`, `--from <путь>` (папка старой установки), `--yes` (без подтверждения).
