---
title: CLI and updates
description: gowave-node commands, updating the node and the Xray core.
sidebar:
  order: 3
---

## Commands

| Command | What it does |
| :--- | :--- |
| `gowave-node status` | Node and core status |
| `gowave-node status --wait-running` | Wait until the management service answers (up to 30 seconds) |
| `gowave-node status --wait-ready` | Wait until the node has its configuration and Xray is running (up to 2 minutes) |
| `gowave-node logs -n 100 -f` | Node log |
| `gowave-node xlogs -n 100 -f` | Xray log |
| `gowave-node restart` | Restart |
| `gowave-node update -y` | Update the node to the latest release |
| `gowave-node core install -y` | Install the latest stable Xray |
| `gowave-node core install --version v26.7.28 -y` | Install a specific Xray version |
| `gowave-node core reset` | Go back from a custom core to the standard one |

Run the commands as root: the CLI finds the node through a private file in `/run/gowave-node`. Installs moved from the old name also keep the `remnanode` and `remnanode-go` commands.

## How the node updates

The node updates from [gowave-node](https://github.com/aaaSaZaN/gowave-node/releases) releases and the core from XTLS/Xray-core releases. If you ask for a version that does not exist, the command fails instead of installing another one. Every download is checked against its published SHA-256 before it replaces anything.

The previous binary is kept. `gowave-node update` waits for the restart in the terminal. When the panel starts an update on systemd, a transient `systemd-run` unit watches the restart and restores the previous binary if the node does not come back.

## Updating from the panel

In a Go node's card, click the Xray Core version: you can pick an official release or pre-release, or paste a direct HTTPS link to a binary or archive. The node version itself is picked on the **GoWave Node Go** tab; the list comes from gowave-node releases.

Panel updates need systemd. On Entware, update the node with `gowave-node update`. On an s6-only host a panel update works only with an external restart supervisor; without one the node rejects the request and keeps the current binary.
