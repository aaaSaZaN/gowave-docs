---
title: Quick start
description: From an empty server to the first subscription.
sidebar:
  order: 1
---

## Requirements

A Linux server, a domain with an A record pointing to it, and root access. See [requirements](../../install/requirements/) for details.

## Step 1. Panel

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)"
```

The installer asks for the database, the domain and the reverse proxy, then sets up HTTPS. For a manual installation, see [Systemd and SQLite](../../install/systemd/) or [Docker Compose and PostgreSQL](../../install/docker/).

## Step 2. Administrator

Open `https://<domain>` right after installing: the first person to open the panel creates the administrator.

## Step 3. Node

Add the node in the panel and install the [Go node](../../install/node/install/) on the server that will carry the traffic. The installer needs the `SECRET_KEY` from the node settings in the panel.

## Step 4. Users

Create a config profile and hosts, then a user. Their subscription link works right away; what each client receives is decided by the [response rules](../../features/subscription-rules/).

## Step 5. Subscription page

Optional. The [subscription page](../../install/subscription-page/) shows users instructions and QR codes and hides the panel's address.

## Moving from another panel

The installer detects Remnawave and PasarGuard on the server and offers to move their data. Manual commands are in the [Migration](../../migration/remnawave/) section.
