---
title: CLI
description: gowave commands for access recovery, imports and migrations.
sidebar:
  order: 1
---

The installer creates the global `gowave` command (`/usr/local/bin/gowave`). With a manual installation create it yourself: `ln -s /opt/gowave/gowave-server /usr/local/bin/gowave`. After `gowave migrate to-docker`, the host `gowave` command forwards calls into the container automatically.

On systemd, run commands as the service user from the panel directory, so new database files belong to that user:

```bash
cd /opt/gowave && sudo -u gowave gowave rescue
```

In Docker, open the menu like this:

```bash
docker exec -it gowave cli
```

Inside the container, `cli` and `rescue` are short names for `/app/gowave rescue`. Run other commands through the binary: `docker exec -it gowave /app/gowave <command>`. The container's root filesystem is read-only, so copy a file the command has to read (a 3x-ui database, a PasarGuard archive) into a separate directory and mount it in a one-off run. The directory must belong to UID 10001, so SQLite can open the database even in WAL mode.

```bash
mkdir -p /root/gowave-import && cp /etc/x-ui/x-ui.db /root/gowave-import/
chown -R 10001:10001 /root/gowave-import
cd /opt/gowave-docker
docker compose run --rm -v /root/gowave-import:/import gowave import 3x-ui /import/x-ui.db
```

## Interactive menu

```bash
gowave rescue
```

`gowave cli` does the same. Menu items:

| # | What it does |
| :--- | :--- |
| 1 | Remove administrators so the first-run setup appears again in the browser |
| 2 | Change an administrator's password |
| 3 | Create an administrator |
| 4 | List administrators |
| 5 | Turn on username/password login |
| 6 | Show the node `SECRET_KEY` |
| 7 | Import from [PasarGuard](../../migration/pasarguard/) |
| 8 | Move from [Remnawave](../../migration/remnawave/) PostgreSQL to SQLite, then offer to remove the old containers |
| 9 | [Move to Docker](../../migration/sqlite-to-docker/) (SQLite to PostgreSQL) |
| 10 | Move from Remnawave PostgreSQL to GoWave PostgreSQL |
| 11 | Import from [3x-ui](../../migration/3x-ui/) |

## Commands

| Command | What it does |
| :--- | :--- |
| `gowave --version` | Panel version |
| `gowave rescue --reset-admin` | Removes administrators so the first-run setup appears again in the browser |
| `gowave rescue --list-admins` | Lists administrators |
| `gowave rescue --enable-password-auth` | Forces username/password login on |
| `gowave rescue --print-secret-key` | Prints the `SECRET_KEY` for connecting nodes |
| `gowave rescue --print-secret-key-raw` | Prints only the key itself, for scripts |
| `gowave rescue --help` | Flag reference |
| `gowave import pasarguard [path\|dsn\|backup.zip]` | Import from [PasarGuard](../../migration/pasarguard/) |
| `gowave import 3x-ui [path]` | Import from [3x-ui](../../migration/3x-ui/), `/etc/x-ui/x-ui.db` by default |
| `gowave migrate pg-to-sqlite [dsn] [file]` | Move from Remnawave's PostgreSQL to SQLite |
| `gowave migrate pg-to-pg [source-dsn] [target-dsn] [--force]` | Move from Remnawave's PostgreSQL to GoWave's PostgreSQL |
| `gowave migrate sqlite-to-pg [file] [dsn] [--force]` | Copy a GoWave SQLite database into an existing PostgreSQL database |
| `gowave migrate to-docker` | Move an SQLite installation to Docker with PostgreSQL. Flags are on [SQLite to Docker](../../migration/sqlite-to-docker/) |
| `gowave service install [directory]` | As root: creates the `gowave` user and the systemd service restrictions, see [Systemd and SQLite](../../install/systemd/#service). The directory defaults to `/opt/gowave` |
| `gowave update apply <directory>` | As root: installs the newest build of the channel. The `gowave-update` service runs it for in-panel updates; you rarely need it by hand |

`--force` in `pg-to-pg` and `sqlite-to-pg` allows replacing data when the target already holds users, nodes or hosts. Without it such a database is left alone.

Without arguments the commands find the source and the target themselves: Remnawave from `/opt/remnawave/.env`, GoWave's PostgreSQL from `DATABASE_URL` in the panel's `.env`, or else from `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` and `POSTGRES_PORT`. Passwords in DSNs are hidden in the output.

See [Migration](../../migration/remnawave/) for details.
