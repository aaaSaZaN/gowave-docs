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

<small>Ansible playbooks repository: [aaaSaZaN/gowave-ansible](https://github.com/aaaSaZaN/gowave-ansible)</small>

The [installer](../../install/installer/) asks for the database, the update channel, the reverse proxy and the domain, then sets up HTTPS. For a manual installation, see [Systemd and SQLite](../../install/systemd/) or [Docker Compose and PostgreSQL](../../install/docker/).

## Step 2. Administrator

Open the address the installer prints (`https://<domain>`, or with your dashboard path) right after installing: the first person to open the panel creates the administrator.

## Step 3. Node

Add the node in the panel and install [GoWave Node](../../install/node/install/) on the server that will carry the traffic. When you add the node, the panel shows a ready install command with the `SECRET_KEY` and the port; run it on the node server.

## Step 4. Users

Create a config profile and hosts, then a user. Their subscription link works right away; what each client receives is decided by the [response rules](../../features/subscription-rules/).

## Step 5. Subscription page

Optional. The [subscription page](../../install/subscription-page/) shows users instructions and QR codes and hides the panel's address.

## Moving from another panel

The installer detects Remnawave and PasarGuard on the server and offers to move their data. Manual commands, including the 3x-ui import, are in the [Migration](../../migration/remnawave/) section.
