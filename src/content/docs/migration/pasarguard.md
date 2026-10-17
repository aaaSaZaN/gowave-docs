---
title: С PasarGuard
description: Импорт пользователей и HWID-устройств из PasarGuard.
sidebar:
  order: 2
---

[Установщик](../../install/installer/) сам находит Remnawave и PasarGuard и предлагает перенос. Команды ниже - для ручного запуска. Исходные базы во всех сценариях только читаются.

```bash
# Найти базу автоматически
gowave import pasarguard

# Или указать путь к файлу или DSN
gowave import pasarguard /opt/pasarguard/data/db.sqlite3
```

- Переносятся пользователи, VLESS UUID, пароли Trojan, Shadowsocks и Hysteria, лимиты трафика, стратегии сброса, заметки и HWID-устройства.
- Пользователи привязываются к скваду по умолчанию.
- База находится по `SQLALCHEMY_DATABASE_URL` из `/opt/pasarguard/.env` (SQLite, PostgreSQL или TimescaleDB, в том числе через pgbouncer) или по файлу `/var/lib/pasarguard/db.sqlite3`. MySQL и MariaDB не поддерживаются.
