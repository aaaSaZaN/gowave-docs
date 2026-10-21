---
title: Requirements
description: What a server needs to run GoWave.
sidebar:
  order: 1
---

:::tip[The short version]
- **CPU:** anything that runs Linux. Most of the time the panel just waits for requests.
- **Memory:** about 50 MB.
- **Disk:** a 28 MB binary, the web interface and a database file.
- **Patience:** 0.2 seconds to start.
:::

## Server

- Linux on `amd64` or `arm64`. The installer supports Debian, Ubuntu and RHEL-family distributions.
- Root access.
- Ports 80 and 443 open for HTTPS. The panel itself listens on `127.0.0.1:3000` only.

## Domain

You need a domain or subdomain whose A record points to the server. The panel is served over HTTPS only, with a certificate for that domain. The [subscription page](../subscription-page/) usually gets another subdomain.

## Memory

The panel runs as a single process and takes about 50 MB under load, see [benchmarks](../../benchmarks/).

| Option | What runs on the server |
| :--- | :--- |
| [Systemd and SQLite](../systemd/) | Only the panel; the database is a file next to it |
| [Docker and PostgreSQL](../docker/) | The panel and PostgreSQL in containers. Under benchmark load PostgreSQL used about 140 MB |

Nodes run on separate servers; their requirements are on the [Go node installation](../node/install/) page. Running the panel and a node on the same server is not recommended: both want port 443, and both default to port `3000`. If you need it anyway, split the traffic yourself, for example with `ssl_preread` in Nginx; see the [basic example](../reverse-proxy/ssl-preread/).
