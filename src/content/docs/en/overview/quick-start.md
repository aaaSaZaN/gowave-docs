---
title: Quick start
description: From an empty server to a working connection.
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

The [installer](../../install/installer/) asks for the database, update channel, reverse proxy, and domain, then sets up HTTPS. For a manual installation, see [Systemd and SQLite](../../install/systemd/) or [Docker Compose and PostgreSQL](../../install/docker/).

## Step 2. Administrator

Open the address printed by the installer (`https://<domain>` or with your dashboard path). Open the panel right after installation: the first visitor creates the administrator account.

## Step 3. Xray config (config profile)

GoWave manages Xray cores through configuration profiles. A profile stores the core's JSON configuration with inbounds and routing rules.

1. Go to "Config profiles" and click "Create profile".
2. In the editor, click the menu button at the bottom (three lines next to "Save") and choose "Load from GitHub". The panel fetches a ready configuration template.
3. In the same editor menu, you can select "Generate key pair".
4. Leave `clients: []` empty: the panel manages clients automatically.
5. Enter a profile name (tag) and save it.

## Step 4. Node

The node runs Xray and proxies client traffic.

1. Go to "Nodes" and click "Add node".
2. In the creation form, enter a name, the node server address, and select your created config profile with its active inbound right away.
3. Copy the installation command with `SECRET_KEY` and run it on the node server as root:

```bash
sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave-node/main/install.sh)"
```

Once the service starts, the node connects to the panel, applies the profile, and starts Xray. The node status will change to "Online".

If the node runs on the same machine as the panel, the [GoWave installer](../../install/installer/#local-node) can set it up locally on port `2222`.

## Step 5. Host

A host links an inbound to the parameters provided to the client.

1. Go to "Hosts" and click "Create host".
2. Select your inbound: the server address and port are filled in automatically. The public key is also managed by the panel automatically.
3. Enter a descriptive remark (for example, `Germany VLESS`) and save the host.

## Step 6. Squad

A squad groups inbounds and grants access to users. Without a squad, a client will not receive connections in their subscription.

1. Go to "Squads" (internal squads) and click "Create squad".
2. Enter a name (for example, `Main`).
3. Check the inbound of the created host and save.

## Step 7. User

1. Go to "Users" and click "Create user".
2. Enter a username, expiration date, and optional traffic limit.
3. Select the created squad in the internal squads list.
4. Save the user. The panel creates a UUID and provisions the client in the Xray core on the node.

## Step 8. Subscription page and client

To allow users to receive working configurations, QR codes, and import profiles into client apps, set up the [subscription page](../../install/subscription-page/). This is the standard way to deliver configs to clients.

1. Deploy the subscription page container following the [guide](../../install/subscription-page/).
2. Open the user's personal link: `https://sub.<your-domain>/<shortUuid>`.
3. Choose the preferred client app (Happ, Streisand, v2rayN, v2rayNG, Nekobox, Shadowrocket) and click "Add to app" or scan the QR code.

Connect to the server and verify internet access.

## Moving from another panel

The installer detects Remnawave and PasarGuard on the server and offers to migrate their data. Manual commands, including the 3x-ui import, are in the [Migration](../../migration/remnawave/) section.
