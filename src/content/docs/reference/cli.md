---
title: CLI
description: Команды gowave - восстановление доступа, импорт и миграции.
sidebar:
  order: 1
---

Глобальную команду `gowave` (`/usr/local/bin/gowave`) создаёт установщик. При ручной установке создайте её сами: `ln -s /opt/gowave/gowave-server /usr/local/bin/gowave`. В Docker команды выполняются внутри контейнера: `docker compose exec gowave /app/gowave <команда>`. После `gowave migrate to-docker` команда `gowave` на хосте сама перенаправляет вызовы в контейнер.

На systemd запускайте команды от пользователя службы из каталога панели, чтобы новые файлы базы принадлежали ему:

```bash
cd /opt/gowave && sudo -u gowave gowave rescue
```

## Интерактивное меню

```bash
gowave rescue
```

Сброс и создание администраторов, импорт из PasarGuard и 3x-ui, миграции баз данных - всё доступно по пунктам меню.

## Команды

| Команда | Что делает |
| :--- | :--- |
| `gowave --version` | Версия панели |
| `gowave rescue --reset-admin` | Удаляет администраторов, чтобы заново пройти первичную настройку в браузере |
| `gowave rescue --list-admins` | Список администраторов |
| `gowave rescue --enable-password-auth` | Принудительно включает вход по логину и паролю |
| `gowave rescue --print-secret-key` | Выводит `SECRET_KEY` для подключения нод |
| `gowave rescue --help` | Справка по флагам |
| `gowave import pasarguard [путь\|dsn]` | Импорт из PasarGuard (SQLite, ZIP-архив или PostgreSQL) |
| `gowave import 3x-ui [путь]` | Импорт клиентов и входящих соединений из 3x-ui (SQLite) |
| `gowave migrate pg-to-pg [исходный_dsn] [целевой_dsn] [--force]` | Перенос напрямую из PostgreSQL Remnawave в PostgreSQL GoWave |
| `gowave migrate pg-to-sqlite [dsn] [файл]` | Перенос из PostgreSQL Remnawave в SQLite |
| `gowave migrate sqlite-to-pg [файл] [целевой_dsn] [--force]` | Перенос базы SQLite GoWave в существующий PostgreSQL |
| `gowave migrate to-docker` | Перевод установки с SQLite в Docker с PostgreSQL |
| `gowave service install [каталог]` | От root: создаёт пользователя `gowave` и ограничения службы systemd, см. [Systemd и SQLite](../../install/systemd/#служба). Каталог по умолчанию `/opt/gowave` |

Подробности о переносах - в разделе [Миграция](../../migration/remnawave/).
