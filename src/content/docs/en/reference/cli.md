---
title: CLI
description: Gowave commands - access recovery, import, and migrations.
sidebar:
  order: 1
---

The global `gowave` command (`/usr/local/bin/gowave`) is created by the installer. For manual installations, create the symlink manually: `ln -s /opt/gowave/gowave-server /usr/local/bin/gowave`. After running `gowave migrate to-docker`, the `gowave` command on the host automatically proxies calls into the container.

The CLI can be executed from any directory. The binary automatically detects the Gowave installation directory (in `/opt/gowave` or via `GOWAVE_INSTALL_DIR`), reads `.env`, and resolves database file ownership and permissions:

```bash
gowave cli
```

`gowave rescue` is an alias and functions identically. Running `cd /opt/gowave && sudo -u gowave` is no longer required.

In Docker, launch the menu inside the container:

```bash
docker exec -it gowave cli
```

Inside the container, `cli` and `rescue` are aliases for `/app/gowave cli`. Execute other commands directly via the binary: `docker exec -it gowave /app/gowave <command>`. Because the container root is read-only, copy files intended for import (such as a 3x-ui database or PasarGuard archive) into a dedicated directory and mount it for a one-off run. The directory must belong to UID 10001 so SQLite can open the file in WAL mode:

```bash
mkdir -p /root/gowave-import && cp /etc/x-ui/x-ui.db /root/gowave-import/
chown -R 10001:10001 /root/gowave-import
cd /opt/gowave-docker
docker compose run --rm -v /root/gowave-import:/import gowave import 3x-ui /import/x-ui.db
```

## Interactive menu

Run without arguments, or with `cli` / `rescue`:

```bash
gowave cli
```

Menu options:

| No. | Description |
| :--- | :--- |
| 1 | Reset superadmin (removes administrators to re-trigger first-time web onboarding) |
| 2 | Reset administrator password |
| 3 | Create a new administrator account |
| 4 | List all administrators |
| 5 | Force-enable username and password authentication |
| 6 | Generate and print `SECRET_KEY` for nodes |
| 7 | Import database from [PasarGuard](../../migration/pasarguard/) (SQLite or PostgreSQL) |
| 8 | Migrate from [Remnawave](../../migration/remnawave/) PostgreSQL to Gowave SQLite (with option to purge old containers) |
| 9 | [Migrate to Docker](../../migration/sqlite-to-docker/) (SQLite to PostgreSQL) |
| 10 | Migrate from Remnawave PostgreSQL directly into Gowave PostgreSQL |
| 11 | Import clients and inbounds from [3x-ui](../../migration/3x-ui/) (SQLite) |

## Commands

| Command | Description |
| :--- | :--- |
| `gowave --version` | Panel version |
| `gowave cli` (or `gowave rescue`) | Launch the interactive CLI menu |
| `gowave rescue --reset-admin` | Delete administrators to restart web setup |
| `gowave rescue --list-admins` | List existing administrators |
| `gowave rescue --enable-password-auth` | Force-enable password login |
| `gowave rescue --print-secret-key` | Print `SECRET_KEY` for connecting nodes |
| `gowave rescue --print-secret-key-raw` | Print only the secret key string without decoration (for scripts) |
| `gowave rescue --db <path>` | Override database path (e.g. `/path/to/gowave.db`) |
| `gowave rescue --keep-root-db` | Preserve root ownership of database files (skip chown to `gowave`) |
| `gowave rescue --help` | Display command help |
| `gowave import pasarguard [path\|dsn\|backup.zip]` | Import from [PasarGuard](../../migration/pasarguard/) |
| `gowave import 3x-ui [path]` | Import from [3x-ui](../../migration/3x-ui/), default `/etc/x-ui/x-ui.db` |
| `gowave migrate pg-to-sqlite [dsn] [file]` | Migrate from Remnawave PostgreSQL to SQLite |
| `gowave migrate pg-to-pg [source_dsn] [target_dsn] [--force]` | Migrate from Remnawave PostgreSQL to Gowave PostgreSQL |
| `gowave migrate sqlite-to-pg [file] [dsn] [--force]` | Copy Gowave SQLite data into an existing PostgreSQL |
| `gowave migrate to-docker` | Migrate SQLite installation to Docker with PostgreSQL. Flags described in [SQLite to Docker](../../migration/sqlite-to-docker/) |
| `gowave service install [directory]` | As root: creates `gowave` user and systemd sandboxing. Default directory `/opt/gowave` |
| `gowave update apply <directory>` | As root: installs latest channel release (invoked by `gowave-update` service) |

The `--force` flag in `pg-to-pg` and `sqlite-to-pg` permits replacing data if the target database already contains users, nodes, or hosts. Without it, populated databases are left unmodified.

When run without arguments, migration commands discover connection details automatically: Remnawave from `/opt/remnawave/.env`, and Gowave PostgreSQL from `DATABASE_URL` in the panel's `.env` (or via `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `POSTGRES_PORT`). Passwords in DSN strings are masked in console output.

Migration guides: [Remnawave migration](../../migration/remnawave/).
