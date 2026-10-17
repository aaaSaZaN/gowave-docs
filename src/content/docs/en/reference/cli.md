---
title: CLI
description: gowave commands for access recovery, imports and migrations.
sidebar:
  order: 1
---

When started as root for the first time, the binary registers the global `gowave` command (`/usr/local/bin/gowave`). In Docker, commands run inside the container: `docker compose exec gowave /app/gowave <command>`. After `gowave migrate to-docker`, the host `gowave` command forwards calls into the container automatically.

## Interactive menu

```bash
gowave rescue
```

Reset and create administrators, run imports and migrations, all from a menu.

## Commands

| Command | What it does |
| :--- | :--- |
| `gowave --version` | Panel version |
| `gowave rescue --reset-admin` | Removes administrators so the first-run setup appears again in the browser |
| `gowave rescue --list-admins` | Lists administrators |
| `gowave rescue --enable-password-auth` | Forces username/password login on |
| `gowave rescue --print-secret-key` | Prints the `SECRET_KEY` for connecting nodes |
| `gowave rescue --help` | Flag reference |
| `gowave import pasarguard [path\|dsn]` | Import from PasarGuard |
| `gowave migrate pg-to-sqlite [dsn] [file]` | Move from Remnawave's PostgreSQL to SQLite |
| `gowave migrate to-docker` | Move an SQLite installation to Docker with PostgreSQL |
| `gowave migrate sqlite-to-pg [file] [dsn] [--force]` | Copy data from SQLite into a running PostgreSQL |

See [Migration](../../migration/remnawave/) for details.

## `sqlite-to-pg`

The low-level copy command that `to-docker` is built on. Before copying it checks SQLite for broken references between tables and refuses to overwrite a PostgreSQL database that already has users, nodes or hosts; `--force` allows it. The copy runs in a single transaction and does not need PostgreSQL superuser rights.
