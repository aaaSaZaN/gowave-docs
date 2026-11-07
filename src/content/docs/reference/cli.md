---
title: CLI
description: Команды gowave - восстановление доступа, импорт и миграции.
sidebar:
  order: 1
---

Глобальную команду `gowave` (`/usr/local/bin/gowave`) создаёт установщик. При ручной установке создайте её сами: `ln -s /opt/gowave/gowave-server /usr/local/bin/gowave`. После `gowave migrate to-docker` команда `gowave` на хосте сама перенаправляет вызовы в контейнер.

На systemd запускайте команды от пользователя службы из каталога панели, чтобы новые файлы базы принадлежали ему:

```bash
cd /opt/gowave && sudo -u gowave gowave rescue
```

В Docker меню открывается так:

```bash
docker exec -it gowave cli
```

Внутри контейнера `cli` и `rescue` - короткие имена для `/app/gowave rescue`. Остальные команды запускайте через бинарник: `docker exec -it gowave /app/gowave <команда>`. Корень контейнера только для чтения, поэтому файл, который команда должна прочитать (база 3x-ui, архив PasarGuard), скопируйте в отдельную папку и подключите её в разовом запуске. Папка должна принадлежать UID 10001: так SQLite сможет открыть базу даже в режиме WAL.

```bash
mkdir -p /root/gowave-import && cp /etc/x-ui/x-ui.db /root/gowave-import/
chown -R 10001:10001 /root/gowave-import
cd /opt/gowave-docker
docker compose run --rm -v /root/gowave-import:/import gowave import 3x-ui /import/x-ui.db
```

## Интерактивное меню

```bash
gowave rescue
```

`gowave cli` - то же самое. Пункты меню:

| № | Что делает |
| :--- | :--- |
| 1 | Удалить администраторов, чтобы заново пройти первичную настройку в браузере |
| 2 | Сменить пароль администратора |
| 3 | Создать администратора |
| 4 | Список администраторов |
| 5 | Включить вход по логину и паролю |
| 6 | Показать `SECRET_KEY` для нод |
| 7 | Импорт из [PasarGuard](../../migration/pasarguard/) |
| 8 | Перенос из PostgreSQL [Remnawave](../../migration/remnawave/) в SQLite, с предложением удалить старые контейнеры |
| 9 | [Переход в Docker](../../migration/sqlite-to-docker/) (SQLite в PostgreSQL) |
| 10 | Перенос из PostgreSQL Remnawave в PostgreSQL GoWave |
| 11 | Импорт из [3x-ui](../../migration/3x-ui/) |

## Команды

| Команда | Что делает |
| :--- | :--- |
| `gowave --version` | Версия панели |
| `gowave rescue --reset-admin` | Удаляет администраторов, чтобы заново пройти первичную настройку в браузере |
| `gowave rescue --list-admins` | Список администраторов |
| `gowave rescue --enable-password-auth` | Принудительно включает вход по логину и паролю |
| `gowave rescue --print-secret-key` | Выводит `SECRET_KEY` для подключения нод |
| `gowave rescue --print-secret-key-raw` | Только сам ключ, без пояснений - для скриптов |
| `gowave rescue --help` | Справка по флагам |
| `gowave import pasarguard [путь\|dsn\|backup.zip]` | Импорт из [PasarGuard](../../migration/pasarguard/) |
| `gowave import 3x-ui [путь]` | Импорт из [3x-ui](../../migration/3x-ui/), по умолчанию `/etc/x-ui/x-ui.db` |
| `gowave migrate pg-to-sqlite [dsn] [файл]` | Перенос из PostgreSQL Remnawave в SQLite |
| `gowave migrate pg-to-pg [dsn-источника] [dsn-цели] [--force]` | Перенос из PostgreSQL Remnawave в PostgreSQL GoWave |
| `gowave migrate sqlite-to-pg [файл] [dsn] [--force]` | Копирование SQLite GoWave в уже существующую базу PostgreSQL |
| `gowave migrate to-docker` | Перевод установки с SQLite в Docker с PostgreSQL. Флаги - на странице [С SQLite на Docker](../../migration/sqlite-to-docker/) |
| `gowave service install [каталог]` | От root: создаёт пользователя `gowave` и ограничения службы systemd, см. [Systemd и SQLite](../../install/systemd/#служба). Каталог по умолчанию `/opt/gowave` |
| `gowave update apply <каталог>` | От root: ставит последнюю сборку канала. Эту команду запускает служба `gowave-update` при обновлении из панели, вручную она обычно не нужна |

`--force` в командах `pg-to-pg` и `sqlite-to-pg` разрешает заменить данные, если в целевой базе уже есть пользователи, ноды или хосты. Без него такая база не трогается.

Без аргументов команды находят источник и цель сами: Remnawave - по `/opt/remnawave/.env`, PostgreSQL GoWave - по `DATABASE_URL` из `.env` панели, а если его нет, по `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` и `POSTGRES_PORT`. В выводе пароли из DSN скрыты.

Подробности о переносах - в разделе [Миграция](../../migration/remnawave/).
