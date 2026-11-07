---
title: From Remnawave
description: Moving data from Remnawave's PostgreSQL to GoWave on SQLite or PostgreSQL.
sidebar:
  order: 1
---

The [installer](../../install/installer/#moving-from-another-panel) detects Remnawave and PasarGuard and offers to move their data. The commands below are for running it manually. Source databases are only ever read.

Both commands find the Remnawave database through `/opt/remnawave/.env` and connect to it on the published port `127.0.0.1:6767`. Pass a DSN as the first argument for any other address. While copying, it is best to stop the `remnawave` container and keep `remnawave-db` running, so nothing writes to it halfway through.

## To SQLite

```bash
gowave migrate pg-to-sqlite
```

- All tables are copied: users, traffic, nodes, hosts, templates, squads.
- The source database and `.env` are not changed. By default the result is `gowave-migrated.sqlite`: set it as `DATABASE_URL` with `DB_DRIVER=sqlite` and restart GoWave. The installer does this for you.
- The interactive menu (`gowave rescue`, item 8) then offers to stop and remove the `remnawave`, `remnawave-db` and `remnawave-redis` containers, but only after you confirm.

## To PostgreSQL

If GoWave already runs on PostgreSQL, for example in [Docker](../../install/docker/), the data goes from database to database without a SQLite hop:

```bash
gowave migrate pg-to-pg
```

Or with explicit addresses:

```bash
gowave migrate pg-to-pg \
  'postgresql://postgres:PASSWORD@127.0.0.1:6767/postgres' \
  'postgresql://gowave:PASSWORD@127.0.0.1:5432/gowave?sslmode=disable'
```

The second address is GoWave's PostgreSQL. A Docker install publishes it on `127.0.0.1:5432`, and the password is `POSTGRES_PASSWORD` in `/opt/gowave-docker/.env`. Run the command on the host, where both databases are reachable. From inside the panel container, Remnawave's port on the host loopback is out of reach.

How the copy works:

- The source is read in a single read-only transaction, so the data is consistent as of the start.
- The target is written in a single transaction: if anything fails, the GoWave database stays as it was.
- If the target already has users, nodes or hosts, the command stops. `--force` allows replacing them.
- The command refuses to copy a database onto itself and does not accept a GoWave database as the source.
- At the end it prints a report: which Remnawave tables and columns GoWave does not store, and which GoWave tables stayed empty.

After the copy, make sure the panel's `.env` has `DB_DRIVER=postgres` and the target `DATABASE_URL` (Docker already does), restart the panel and log in with your existing administrator. Stop the old panel once you are sure everything is there.

When you pick "PostgreSQL in Docker", the installer does the same through [`gowave migrate to-docker --from-upstream`](../sqlite-to-docker/#flags): it creates the Docker project and copies Remnawave straight into its PostgreSQL.
