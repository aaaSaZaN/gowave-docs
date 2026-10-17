---
title: CLI and updates
description: remnanode commands, updating the node and the Xray core.
sidebar:
  order: 3
---

## Commands

| Command | What it does |
| :--- | :--- |
| `remnanode status` | Node and core status |
| `remnanode status --wait-ready` | Wait until the node has its configuration and Xray is running |
| `remnanode logs -n 100 -f` | Node log |
| `remnanode xlogs -n 100 -f` | Xray log |
| `remnanode restart` | Restart |
| `remnanode update -y` | Update the node to the latest release |
| `remnanode core install -y` | Install the latest stable Xray |
| `remnanode core install --version v26.7.28 -y` | Install a specific Xray version |
| `remnanode core reset` | Go back from a custom core to the standard one |

Run the commands as the service user, usually root: the CLI finds the node through a private file in `/run/remnanode`.

## Updating from the panel

In a Go node's card, click the Xray Core version: you can pick an official release or pre-release, or paste a direct HTTPS link to a binary or archive. The node version itself is picked on the **Remnanode Go** tab; the list comes from remnanode-go releases.

## How updates work

- New node versions come from `aaaSaZaN/remnanode-go`, the core from stable `XTLS/Xray-core` releases. When a specific version is requested, nothing else is installed in its place.
- Every downloaded file is checked against its published checksum before it replaces anything.
- The previous binary is kept. For panel updates on systemd the node watches the restart itself and brings the old version back if the new one does not come up.
- On an s6-only server (as in the original container) panel updates need an external restart supervisor. Without one the node refuses the update and keeps the current version.

Running the installer again also updates the node, see [installation](../install/).
