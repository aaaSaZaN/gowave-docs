---
title: Comparison with Remnawave
description: How GoWave differs from the original Remnawave backend.
sidebar:
  order: 3
---

GoWave replaces the Remnawave backend and keeps its API. The differences are in how it works inside and in what it adds on top.

| | GoWave | Remnawave |
| :--- | :--- | :--- |
| Language | Go | TypeScript (Node.js) |
| Processes | One | Three: API, queue workers, scheduler |
| Database | SQLite or PostgreSQL | PostgreSQL and Valkey (Redis) |
| Memory under load | about 60 MB | about 1 GB |
| API ready after start | 0.21 s | 7.1 s |
| API | All 218 `@remnawave/backend-contract` 3.4.15 commands | Reference |
| Web interface | The Remnawave interface | Its own |
| Nodes | Go node and `remnawave/node` | `remnawave/node`; the Go node connects too |
| Installation | One-command installer, binary or Docker | Docker Compose |
| Updates | A button in the panel (systemd) or `docker compose pull` | `docker compose pull` |

Memory and startup were measured on the same setup; the methodology is on the [benchmarks](../../benchmarks/) page.

## Only in GoWave

- Running without Docker: one binary and an SQLite database.
- An [installer](../../overview/quick-start/) that sets up HTTPS and moves data from Remnawave and PasarGuard.
- [Moving from SQLite to PostgreSQL](../../migration/sqlite-to-docker/) in one command, with rollback on failure.
- Importing from [PasarGuard](../../migration/pasarguard/).

## What works differently

- **Regular expressions** in [response rules](../../features/subscription-rules/) and [templates](../../features/templates/) use RE2 (Go) syntax rather than JavaScript. Lookahead, lookbehind and backreferences are not supported, so a Remnawave rule that uses them stops matching in GoWave.
- **Docker updates** are not started from the panel: it shows the command to run on the server, see [updating](../../install/updating/).

## What is compatible

- **API.** Endpoints, request and response formats, error codes and statuses follow `@remnawave/backend-contract`. The web interface is the Remnawave frontend.
- **Subscriptions.** Output for Xray JSON, Mihomo, sing-box, base64 and other clients is compared with reference output from the original backend.
- **Nodes.** The original `remnawave/node` and the [Go node](../../install/node/install/).
- **The subscription page** `remnawave/subscription-page`.
- **Bots and integrations** that use the Remnawave API with a token.

## What GoWave adds to the API

Endpoints outside the contract serve the GoWave web interface; Remnawave clients and bots do not call them. The [API reference](../../../api/) groups them under **GoWave extensions**:

- `GET /api/nodes/traffic-summary` - each node's lifetime traffic, which the monthly reset does not clear;
- `GET /api/nodes/{uuid}/logs`, `GET /api/nodes/{uuid}/updates` and `POST /api/nodes/{uuid}/updates/apply` - logs and updates of the [Go node](../../install/node/cli/);
- `GET /api/system/updates/check` and `POST /api/system/updates/apply` - [panel updates](../../install/updating/) on systemd;
- `POST /api/system/actions/restore` - restore from a backup.

`PATCH /api/nodes` accepts `trafficTrackingStart`, a field the contract does not have. It sets where the counter starts when the update turns traffic tracking on: `keep` keeps what was counted since the last reset (as Remnawave does), `zero` starts from nothing, `period` recounts the current period from the history.

Yandex sign-in is removed. The `yandex` fields in the OAuth settings remain for contract compatibility, but the provider is always disabled and the panel discards saved credentials.

## How it is verified

- Tests compare the route list with the contract and validate real handler responses against the contract's JSON schemas on both SQLite and PostgreSQL in every CI run.
- Subscription output is compared with committed reference fixtures captured from the original backend.

## Where things are documented

GoWave subscriptions are covered here: [response rules](../../features/subscription-rules/), [Xray JSON, Mihomo and sing-box templates](../../features/templates/), [variables](../../features/template-variables/). Config profiles are regular Xray configs, so protocols and transports follow the [Xray documentation](https://xtls.github.io/config/).
