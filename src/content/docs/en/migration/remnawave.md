---
title: From Remnawave
description: Moving data from Remnawave's PostgreSQL to GoWave.
sidebar:
  order: 1
---

The [installer](../../install/installer/) detects Remnawave and PasarGuard and offers to move their data. The commands below are for running it manually. Source databases are only ever read.

From Remnawave's PostgreSQL to an SQLite file:

```bash
gowave migrate pg-to-sqlite
```

- Connection settings are found in `/opt/remnawave/.env`.
- All tables are copied: users, traffic, nodes, hosts, templates, squads.
- The source database and `.env` are not changed. By default the result is `gowave-migrated.sqlite`: set it as `DATABASE_URL` with `DB_DRIVER=sqlite` and restart GoWave. The installer does this for you.
- The interactive menu (`gowave rescue`) then offers to stop and remove the `remnawave`, `remnawave-db` and `remnawave-redis` containers, but only after you confirm.
