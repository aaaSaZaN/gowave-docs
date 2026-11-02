---
title: From PasarGuard
description: Importing users, squads and profiles from PasarGuard.
sidebar:
  order: 2
---

The [installer](../../overview/quick-start/) detects PasarGuard and offers to migrate data. The commands below are for manual execution. Source databases are only ever read.

```bash
# Auto-detect database
gowave import pasarguard

# Specify path to SQLite file or ZIP backup
gowave import pasarguard /opt/pasarguard/data/db.sqlite3
gowave import pasarguard /path/to/backup.zip

# Or provide PostgreSQL DSN
gowave import pasarguard 'postgresql://user:pass@localhost/pasarguard'
```

- Migrates users, VLESS UUIDs, passwords for Trojan, Shadowsocks and Hysteria, traffic limits, reset strategies, notes, last used timestamps and HWID devices.
- Migrates Xray profiles, inbounds, user groups and squads, host settings, nodes and traffic history.
- Auto-detects database via `SQLALCHEMY_DATABASE_URL` in `/opt/pasarguard/.env` (SQLite, PostgreSQL, TimescaleDB, including PgBouncer) or `/var/lib/pasarguard/db.sqlite3`.
- When importing a ZIP archive, `db.sqlite3` must be at the root of the archive.
