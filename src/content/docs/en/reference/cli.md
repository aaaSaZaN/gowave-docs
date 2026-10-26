---
title: CLI
description: gowave commands for access recovery, imports and migrations.
sidebar:
  order: 1
---

The installer creates the global `gowave` command (`/usr/local/bin/gowave`). With a manual installation create it yourself: `ln -s /opt/gowave/gowave-server /usr/local/bin/gowave`. In Docker, commands run inside the container: `docker compose exec gowave /app/gowave <command>`. After `gowave migrate to-docker`, the host `gowave` command forwards calls into the container automatically.

On systemd, run commands as the service user from the panel directory, so new database files belong to that user:

```bash
cd /opt/gowave && sudo -u gowave gowave rescue
```

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
| `gowave service install [directory]` | As root: creates the `gowave` user and the systemd service restrictions, see [Systemd and SQLite](../../install/systemd/#service). The directory defaults to `/opt/gowave` |

See [Migration](../../migration/remnawave/) for details.
