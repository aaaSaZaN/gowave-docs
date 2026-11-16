---
title: CLI
description: Команды gowave - восстановление доступа, импорт и миграции.
sidebar:
  order: 1
---

Глобальную команду `gowave` (`/usr/local/bin/gowave`) создаёт установщик. При ручной установке настройте симлинк: `ln -s /opt/gowave/gowave-server /usr/local/bin/gowave`. После `gowave migrate to-docker` команда `gowave` на хосте сама перенаправляет вызовы в контейнер.

Команда доступна из любого каталога. Бинарник сам находит установку GoWave (в `/opt/gowave` или по переменной `GOWAVE_INSTALL_DIR`), подтягивает `.env` и автоматически выставляет нужные права на файлы базы данных:

```bash
gowave cli
```

`gowave rescue` работает точно так же. Запускать через `cd /opt/gowave && sudo -u gowave` больше не требуется.

В Docker консоль открывается через контейнер:

```bash
docker exec -it gowave cli
```

Внутри контейнера `cli` и `rescue` - короткие алиасы для `/app/gowave cli`. Остальные команды запускайте через бинарник: `docker exec -it gowave /app/gowave <команда>`. Корень контейнера доступен только для чтения, поэтому файл для импорта (база 3x-ui, архив PasarGuard) скопируйте в отдельную папку и подключите её в разовом запуске. Папка должна принадлежать UID 10001: так SQLite сможет открыть базу даже в режиме WAL.

```bash
mkdir -p /root/gowave-import && cp /etc/x-ui/x-ui.db /root/gowave-import/
chown -R 10001:10001 /root/gowave-import
cd /opt/gowave-docker
docker compose run --rm -v /root/gowave-import:/import gowave import 3x-ui /import/x-ui.db
```

## Интерактивное меню

Запуск без параметров или с аргументом `cli` / `rescue`:

```bash
gowave cli
```

Пункты меню:

| № | Что делает |
| :--- | :--- |
| 1 | Сбросить супер-администратора (удаляет админов для повторного прохождения первичной настройки в браузере) |
| 2 | Сменить пароль администратора |
| 3 | Создать новую учётную запись администратора |
| 4 | Список всех существующих администраторов |
| 5 | Принудительно включить вход по логину и паролю |
| 6 | Сгенерировать и показать `SECRET_KEY` для нод |
| 7 | Импорт базы из [PasarGuard](../../migration/pasarguard/) (SQLite или PostgreSQL) |
| 8 | Перенос из PostgreSQL [Remnawave](../../migration/remnawave/) в SQLite GoWave (с предложением удалить старые контейнеры) |
| 9 | [Переход в Docker](../../migration/sqlite-to-docker/) (миграция SQLite в PostgreSQL) |
| 10 | Перенос из PostgreSQL Remnawave напрямую в PostgreSQL GoWave |
| 11 | Импорт клиентов и входящих соединений из [3x-ui](../../migration/3x-ui/) (SQLite) |

## Команды

| Команда | Что делает |
| :--- | :--- |
| `gowave --version` | Версия панели |
| `gowave cli` (или `gowave rescue`) | Запуск интерактивного меню управления |
| `gowave rescue --reset-admin` | Удаляет администраторов, чтобы заново пройти первичную настройку в браузере |
| `gowave rescue --list-admins` | Список всех администраторов |
| `gowave rescue --enable-password-auth` | Принудительно включает вход по логину и паролю |
| `gowave rescue --print-secret-key` | Выводит `SECRET_KEY` для подключения нод |
| `gowave rescue --print-secret-key-raw` | Только сам ключ, без пояснений - для скриптов |
| `gowave rescue --db <путь>` | Явное указание пути к базе данных (например, `/path/to/gowave.db`) |
| `gowave rescue --keep-root-db` | Сохранить права `root` на файл базы данных (не менять владельца на пользователя `gowave`) |
| `gowave rescue --help` | Справка по всем доступным флагам |
| `gowave import pasarguard [путь\|dsn\|backup.zip]` | Импорт из [PasarGuard](../../migration/pasarguard/) |
| `gowave import 3x-ui [путь]` | Импорт из [3x-ui](../../migration/3x-ui/), по умолчанию `/etc/x-ui/x-ui.db` |
| `gowave migrate pg-to-sqlite [dsn] [файл]` | Перенос из PostgreSQL Remnawave в SQLite |
| `gowave migrate pg-to-pg [dsn-источника] [dsn-цели] [--force]` | Перенос из PostgreSQL Remnawave в PostgreSQL GoWave |
| `gowave migrate sqlite-to-pg [файл] [dsn] [--force]` | Копирование SQLite GoWave в уже существующую базу PostgreSQL |
| `gowave migrate to-docker` | Перевод установки с SQLite в Docker с PostgreSQL. Флаги - на странице [С SQLite на Docker](../../migration/sqlite-to-docker/) |
| `gowave service install [каталог]` | От root: создаёт пользователя `gowave` и ограничения службы systemd, см. [Systemd и SQLite](../../install/systemd/#служба). Каталог по умолчанию `/opt/gowave` |
| `gowave update apply <каталог>` | От root: ставит последнюю сборку канала. Эту команду запускает служба `gowave-update` при обновлении из панели, вручную она обычно не нужна |

Флаг `--force` в командах `pg-to-pg` и `sqlite-to-pg` разрешает заменить данные, если в целевой базе уже есть пользователи, ноды или хосты. Без него такая база не трогается.

Без аргументов команды находят источник и цель сами: Remnawave - по `/opt/remnawave/.env`, PostgreSQL GoWave - по `DATABASE_URL` из `.env` панели, а если его нет, по `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` и `POSTGRES_PORT`. В выводе пароли из DSN скрыты.

Подробности о переносах - в разделе [Миграция](../../migration/remnawave/).
