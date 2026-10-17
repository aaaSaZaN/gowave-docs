---
title: Components
description: What a GoWave installation is made of.
sidebar:
  order: 2
---

## Panel

The GoWave backend is written in Go and runs as a single process. It serves the API and subscriptions and runs background work: node sync, traffic collection, notifications, Prometheus metrics. Install it with the [installer](../../install/installer/), as a binary with [systemd](../../install/systemd/) or in [Docker](../../install/docker/).

## Web interface

The same interface as Remnawave. These are static files served by the panel from `frontend/dist` next to the binary; in Docker they are part of the image.

## Database

SQLite (a single file, no separate server) or PostgreSQL. Moving from SQLite to PostgreSQL in Docker takes [one command](../../migration/sqlite-to-docker/).

## Node

A server with the Xray core that carries user traffic. It runs the [Go node](../../install/node/install/); the original `remnawave/node` image works too. The panel connects to the node over mTLS and sends it users and configuration.

## Subscription page

The official `remnawave/subscription-page` image. It shows users how to connect and hides the panel's address. It runs next to the panel or on a separate server, see [subscription page](../../install/subscription-page/).

## Reverse proxy

Caddy or Nginx in front of the panel: they accept HTTPS and pass requests to `127.0.0.1:3000`. See [Reverse proxy](../../install/reverse-proxy/overview/).
