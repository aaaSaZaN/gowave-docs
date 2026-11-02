---
title: С PasarGuard
description: Импорт пользователей, сквадов и профилей из PasarGuard.
sidebar:
  order: 2
---

Установщик сам находит PasarGuard и предлагает перенос. Команды ниже нужны для ручного запуска. База источника читается без изменения исходных данных.

```bash
# Найти базу автоматически
gowave import pasarguard

# Указать путь к SQLite или ZIP-архиву с бэкапом
gowave import pasarguard /opt/pasarguard/data/db.sqlite3
gowave import pasarguard /path/to/backup.zip

# Или передать DSN базы PostgreSQL
gowave import pasarguard 'postgresql://user:pass@localhost/pasarguard'
```

- Переносятся пользователи, VLESS UUID, пароли Trojan, Shadowsocks и Hysteria, лимиты трафика, стратегии сброса, заметки, даты использования и привязанные HWID-устройства.
- Переносятся профили Xray, входящие соединения, группы пользователей и сквады, параметры хостов, ноды и история трафика.
- База источника определяется автоматически по переменной `SQLALCHEMY_DATABASE_URL` в `/opt/pasarguard/.env` (поддерживаются SQLite, PostgreSQL и TimescaleDB, включая подключения через PgBouncer) либо по файлу `/var/lib/pasarguard/db.sqlite3`.
- При импорте архива ZIP файл `db.sqlite3` должен лежать в корне архива.
