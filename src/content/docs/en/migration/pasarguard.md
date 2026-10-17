---
title: From PasarGuard
description: Importing users and HWID devices from PasarGuard.
sidebar:
  order: 2
---

The [installer](../../install/installer/) detects Remnawave and PasarGuard and offers to move their data. The commands below are for running it manually. Source databases are only ever read.

```bash
# Find the database automatically
gowave import pasarguard

# Or pass a file path or DSN
gowave import pasarguard /opt/pasarguard/data/db.sqlite3
```

- Users, VLESS UUIDs, Trojan, Shadowsocks and Hysteria passwords, traffic limits, reset strategies, notes and HWID devices are imported.
- Users are attached to the default squad.
- The database is found via `SQLALCHEMY_DATABASE_URL` in `/opt/pasarguard/.env` (SQLite, PostgreSQL or TimescaleDB, including through pgbouncer) or the `/var/lib/pasarguard/db.sqlite3` file. MySQL and MariaDB are not supported.
