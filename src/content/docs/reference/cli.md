---
title: CLI
description: Команды gowave - восстановление доступа, импорт и миграции.
sidebar:
  order: 1
---

При первом запуске от root бинарник регистрирует глобальную команду `gowave` (`/usr/local/bin/gowave`). В Docker команды выполняются внутри контейнера: `docker compose exec gowave /app/gowave <команда>`. После `gowave migrate to-docker` команда `gowave` на хосте сама перенаправляет вызовы в контейнер.

## Интерактивное меню

```bash
gowave rescue
```

Сброс и создание администраторов, импорт, миграции - всё по пунктам.

## Команды

| Команда | Что делает |
| :--- | :--- |
| `gowave --version` | Версия панели |
| `gowave rescue --reset-admin` | Удаляет администраторов, чтобы заново пройти первичную настройку в браузере |
| `gowave rescue --list-admins` | Список администраторов |
| `gowave rescue --enable-password-auth` | Принудительно включает вход по логину и паролю |
| `gowave rescue --print-secret-key` | Выводит `SECRET_KEY` для подключения нод |
| `gowave rescue --help` | Справка по флагам |
| `gowave import pasarguard [путь\|dsn]` | Импорт из PasarGuard |
| `gowave migrate pg-to-sqlite [dsn] [файл]` | Перенос из PostgreSQL Remnawave в SQLite |
| `gowave migrate to-docker` | Перевод установки с SQLite в Docker с PostgreSQL |
| `gowave migrate sqlite-to-pg [файл] [dsn] [--force]` | Копирование данных из SQLite в уже запущенный PostgreSQL |

Подробности о переносах - в разделе [Миграция](../../migration/remnawave/).

## `sqlite-to-pg`

Низкоуровневая команда копирования, на ней построен `to-docker`. Перед копированием она проверяет SQLite на битые ссылки между таблицами и не трогает PostgreSQL, где уже есть пользователи, ноды или хосты. С флагом `--force` такая база будет перезаписана. Копирование идёт в одной транзакции и не требует прав суперпользователя PostgreSQL.
