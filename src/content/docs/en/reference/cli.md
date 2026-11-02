---
title: CLI
description: Commands for gowave - rescue, imports and migrations.
sidebar:
  order: 1
---

The installer creates the global `gowave` command (`/usr/local/bin/gowave`). For manual installations, create the symlink yourself: `ln -s /opt/gowave/gowave-server /usr/local/bin/gowave`. In Docker, run commands inside the container: `docker compose exec gowave /app/gowave <command>`. After `gowave migrate to-docker`, the host's `gowave` command redirects calls into the container automatically.

On systemd, run commands as the service user from the panel's directory so new database files are owned by it:

```bash
cd /opt/gowave && sudo -u gowave gowave rescue
```

## Interactive menu

```bash
gowave rescue
```

Admin resets, PasarGuard and 3x-ui imports, database migrations - all available as menu options.

## Commands

| Command | What it does |
| :--- | :--- |
| `gowave --version` | Panel version |
| `gowave rescue --reset-admin` | Removes administrators to restart the initial web setup |
| `gowave rescue --list-admins` | Lists administrators |
| `gowave rescue --enable-password-auth` | Forces username and password login |
| `gowave rescue --print-secret-key` | Prints the `SECRET_KEY` for connecting nodes |
| `gowave rescue --help` | Flag reference |
| `gowave import pasarguard [path\|dsn]` | Import from PasarGuard (SQLite, ZIP archive or PostgreSQL) |
| `gowave import 3x-ui [path]` | Import clients and inbounds from 3x-ui (SQLite) |
| `gowave migrate pg-to-pg [source_dsn] [target_dsn] [--force]` | Migrate directly from Remnawave PostgreSQL to GoWave PostgreSQL |
| `gowave migrate pg-to-sqlite [dsn] [file]` | Migrate from Remnawave PostgreSQL to SQLite |
| `gowave migrate sqlite-to-pg [file] [target_dsn] [--force]` | Migrate GoWave SQLite data into an existing PostgreSQL |
| `gowave migrate to-docker` | Move this SQLite installation to Docker with PostgreSQL |
| `gowave service install [directory]` | As root: creates the `gowave` user and systemd sandbox, see [Systemd and SQLite](../../install/systemd/#service). Default directory is `/opt/gowave` |

For more details on migration, see [Migration](../../migration/remnawave/).
