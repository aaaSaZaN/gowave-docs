---
title: From 3x-ui
description: Importing clients, credentials and inbounds from a 3x-ui database.
sidebar:
  order: 3
---

Migrating from 3x-ui moves VLESS, Trojan and Shadowsocks clients directly into GoWave. Data is read directly from the panel's SQLite database file.

## Preparation

Before starting, stop the 3x-ui service so the database does not change during the read:

```bash
systemctl stop x-ui
```

Make a backup of the GoWave database. The import runs in a single transaction: if any error occurs, GoWave rolls back to its original state.

## Running the import

If the database is in the default location `/etc/x-ui/x-ui.db`, the path is optional:

```bash
# Default path: /etc/x-ui/x-ui.db
gowave import 3x-ui

# Or with an explicit file path
gowave import 3x-ui /etc/x-ui/x-ui.db
```

The import is also available in `gowave rescue` (option 11).

## What is migrated

- Credentials: UUIDs for VLESS, passwords for Trojan and Shadowsocks.
- Limits and traffic reset: byte values, reset periods (day, week, month, year, or no reset).
- Expiration dates: absolute timestamps. If expired, the status becomes `EXPIRED`. If bandwidth is exceeded, the status becomes `LIMITED`.
- Identifiers: Telegram IDs and client comments.
- Subscription tokens (`subId`). If multiple clients share a token, the first keeps it and subsequent clients receive new unique tokens.
- Traffic statistics: upload, download, total usage and last online timestamp from `client_traffics`.
- Inbounds: converted into GoWave config profiles and internal squads named `3x-ui-<id>-<tag>`.

## Manual steps after import

1. **Nodes.** Install GoWave Node on servers carrying traffic and connect them to the panel.
2. **Hosts.** Create public hosts and attach them to the imported squads.
3. **Subscription links.** Provide new subscription links to clients whose tokens or panel domains changed.
4. **Device limits.** IP limits from 3x-ui do not convert to HWID; configure device limits in GoWave.
5. **Deferred activation.** Clients with deferred expiry (negative timestamps) cause the import to roll back. Activate or remove them in 3x-ui before importing.
