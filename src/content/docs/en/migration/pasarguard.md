---
title: From PasarGuard
description: Importing users, profiles, nodes and history from PasarGuard.
sidebar:
  order: 2
---

The [installer](../../install/installer/#moving-from-another-panel) detects PasarGuard and offers to move its data. The commands below are for running it manually. Source databases are only ever read.

Before importing, stop writes to PasarGuard and back up the GoWave database. If in doubt, import into a separate test database first. Run the command from the panel directory so it picks up GoWave's `.env`.

```bash
# Find the database automatically
gowave import pasarguard

# SQLite file
gowave import pasarguard /opt/pasarguard/data/db.sqlite3

# PasarGuard backup
gowave import pasarguard /root/pasarguard-backup.zip

# PostgreSQL or TimescaleDB
gowave import pasarguard 'postgresql://user:password@localhost/pasarguard'
```

Without an argument the database is found via `SQLALCHEMY_DATABASE_URL` in `/opt/pasarguard/.env` (SQLite, PostgreSQL or TimescaleDB, including through pgbouncer) or the `/var/lib/pasarguard/db.sqlite3` file. MySQL and MariaDB are not supported. In a ZIP backup, `db.sqlite3` must sit at the root; nested older copies are not read. The DSN password is never printed to the log.

The import writes to GoWave in a single transaction, so an error changes nothing. In the `gowave rescue` menu it is item 7.

## What is imported

- Users: VLESS UUIDs, Trojan, Shadowsocks and Hysteria passwords, traffic limits and reset strategies, expiry, notes, subscription revocation, current and lifetime traffic, last online time.
- HWID devices and when they were last used.
- Xray profiles (`core_configs`) and their inbounds.
- Groups, as internal squads, with their user and inbound links. If the database has no groups, users go to GoWave's first squad.
- The main host settings.
- Nodes, node and user traffic history, subscription request history.

Numeric IDs are reassigned; the links between records are kept.

## Importing again

You can run the import again, for example right before the final switch. Users are updated by username, everything else by stable identifiers the import derives from PasarGuard IDs. The data is replaced with the source's current state. Do not rename imported records between runs, or the next run creates duplicates.

## What you finish by hand

- **Nodes** are imported disabled: PasarGuard certificates and API keys do not work with GoWave. Install [GoWave Node](../../install/node/install/) on the servers and enable the nodes in the panel.
- **`on_hold` users** become disabled. Set up delayed activation again.
- **Subscription links** change: GoWave creates its own identifiers, so old PasarGuard links stop working. Send users their new links.
- Not imported: administrators, roles and permissions, JWT, API keys, notifications, panel settings, subscription templates of another engine, renewal plans and host settings with no GoWave counterpart.
