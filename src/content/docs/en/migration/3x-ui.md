---
title: From 3x-ui
description: Importing clients, inbounds and traffic from a 3x-ui database.
sidebar:
  order: 3
---

GoWave reads a 3x-ui database (SQLite) and imports its clients and inbounds. The installer does not offer this import; it is a separate command. The schema was checked against the 3x-ui v2.8.5 sources, and the import has seen few real databases so far, so try it on a test GoWave database first.

Before importing, stop 3x-ui (`x-ui stop`) and back up the GoWave database. Run the command from the panel directory:

```bash
# /etc/x-ui/x-ui.db by default
gowave import 3x-ui

# Another path
gowave import 3x-ui /root/x-ui.db
```

In the `gowave rescue` menu it is item 11. To run the import when the panel is in Docker, see the [CLI reference](../../reference/cli/).

The import writes to GoWave in a single transaction. Any error rolls everything back and leaves the GoWave database as it was.

## What is imported

Each inbound becomes a configuration profile holding just that inbound, plus an internal squad named `3x-ui-<id>-<tag>`. The inbound's clients become users in that squad.

| In 3x-ui | In GoWave |
| :--- | :--- |
| Client `email` | Username. Without an email, `3xui_<inbound>_<number>` |
| UUID (VLESS), password (Trojan, Shadowsocks) | The same credentials |
| `totalGB` | Traffic limit. In the 3x-ui database this is already bytes, despite the name |
| `expiryTime` | Expiry (from milliseconds). None means no expiry |
| Client and inbound `enable` | Status: disabled becomes `DISABLED`, expired `EXPIRED`, over the limit `LIMITED` |
| `reset` of 1, 7, 30, 365 days | Traffic reset every day, week, month, year |
| `tgId`, `comment` | Telegram ID, description |
| `subId` | Subscription short UUID |
| `client_traffics` | Used and lifetime traffic, last online time |

## Limitations

- Only VLESS, Trojan and Shadowsocks are supported. An inbound with another protocol rolls back the whole import.
- A client with a delayed expiry (negative `expiryTime`, counted from the first connection) also rolls back the import. Activate such clients or give them a fixed expiry before importing.
- If one email appears in several inbounds with different credentials, the import rolls back. Give those clients different emails.
- Clients sharing a `subId`: the first keeps it, the others get a separate token and need new links. A kept `subId` keeps the old token, but the old link's domain and path may need reverse proxy changes.
- IP limits are not turned into HWID limits. Other reset periods, panel settings, admin logins and the external Nginx from x-ui-pro are moved by hand.

Before going live, create public hosts for the profiles and connect [GoWave Node](../../install/node/install/) to the servers where Xray ran.
