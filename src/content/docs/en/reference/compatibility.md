---
title: Remnawave compatibility
description: What is compatible with the Remnawave ecosystem and how it is verified.
sidebar:
  order: 3
---

GoWave is a replacement for the Remnawave backend, not a new panel. Anything that works with Remnawave should work with GoWave.

## What is compatible

- **API.** Endpoints, request and response formats, error codes and statuses follow `@remnawave/backend-contract`. The web interface is the Remnawave frontend.
- **Subscriptions.** Output for Xray JSON, Mihomo, sing-box, base64 and other clients is compared with reference output from the original backend.
- **Nodes.** The original `remnawave/node` and the [Go node](../../install/node/install/).
- **The subscription page** `remnawave/subscription-page`.
- **Bots and integrations** that use the Remnawave API with a token.

## How it is verified

- Tests compare the route list with the contract and validate real handler responses against the contract's JSON schemas on both SQLite and PostgreSQL in every CI run.
- Subscription output is compared with committed reference fixtures captured from the original backend.

## Where things are documented

GoWave subscriptions are covered here: [response rules](../../features/subscription-rules/), [Xray JSON, Mihomo and sing-box templates](../../features/templates/), [variables](../../features/template-variables/). Config profiles are regular Xray configs, so protocols and transports follow the [Xray documentation](https://xtls.github.io/config/).
