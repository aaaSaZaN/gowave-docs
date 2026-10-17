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
| Memory under load | about 50 MB | about 1 GB |
| API ready after start | 0.2 s | 4.8 s |
| API | All 218 `@remnawave/backend-contract` 3.4.15 commands | Reference |
| Web interface | The Remnawave interface | Its own |
| Nodes | Go node and `remnawave/node` | `remnawave/node`; the Go node connects too |
| Installation | One-command installer, binary or Docker | Docker Compose |
| Updates | A button in the panel (systemd) or `docker compose pull` | `docker compose pull` |

Memory and startup were measured on the same setup; the methodology is on the [benchmarks](../../benchmarks/) page.

## Only in GoWave

- Running without Docker: one binary and an SQLite database.
- An [installer](../../install/installer/) that sets up HTTPS and moves data from Remnawave and PasarGuard.
- [Moving from SQLite to PostgreSQL](../../migration/sqlite-to-docker/) in one command, with rollback on failure.
- Importing from [PasarGuard](../../migration/pasarguard/).

## What works differently

- **Regular expressions** in [response rules](../../features/subscription-rules/) and [templates](../../features/templates/) use RE2 (Go) syntax rather than JavaScript. Lookahead, lookbehind and backreferences are not supported, so a Remnawave rule that uses them stops matching in GoWave.
- **Docker updates** are not started from the panel: it shows the command to run on the server, see [updating](../../install/updating/).

## How compatibility is checked

Tests compare routes with the contract and validate responses against the contract's JSON schemas on SQLite and PostgreSQL. Subscription output is compared with reference output from the original backend; details are in [compatibility](../../reference/compatibility/).
