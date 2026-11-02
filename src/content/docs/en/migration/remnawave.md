---
title: From Remnawave
description: Moving data from Remnawave PostgreSQL into GoWave.
sidebar:
  order: 1
---

The [installer](../../overview/quick-start/) detects Remnawave and offers to migrate data automatically. When installing with Docker, it copies data directly from Remnawave PostgreSQL into GoWave PostgreSQL without an intermediate SQLite file. Source databases are only ever read.

The commands below are for manual execution.

## Direct PostgreSQL to PostgreSQL

Reads Remnawave's database and writes into GoWave PostgreSQL in a single transaction:

```bash
# Credentials are discovered automatically
gowave migrate pg-to-pg

# Or specify source and target DSN explicitly
gowave migrate pg-to-pg 'postgresql://rw:pass@127.0.0.1:5432/remnawave' 'postgresql://gw:pass@127.0.0.1:5432/gowave'
```

Pass `--force` to overwrite existing users, nodes or hosts in the target database.

Migration details:

- The source database is read inside a repeatable-read transaction. It is never modified.
- The target database is written in a single transaction. Any failure rolls back all changes.
- Safety check: database fingerprints are compared to prevent migrating a database onto itself.
- Types like UUID, JSON, arrays and enums are transferred safely via text format casts.
- NULL values for non-pointer Go model fields are converted to zero values.
- Upstream containers keep running until migration finishes. Verify GoWave first, then stop the old containers.

## From PostgreSQL to SQLite

If GoWave runs on systemd and stores data in a file:

```bash
gowave migrate pg-to-sqlite
```

- Connection settings are read from `/opt/remnawave/.env`.
- All tables are copied: users, traffic, nodes, hosts, templates, squads.
- Creates `gowave-migrated.sqlite` by default. Point `DATABASE_URL` to it with `DB_DRIVER=sqlite` and restart GoWave.

## Rescue menu

Both options are available in the interactive rescue menu:

```bash
gowave rescue
```

- Option 8: migrate from Remnawave PostgreSQL to SQLite.
- Option 10: migrate directly from Remnawave PostgreSQL to GoWave PostgreSQL.
