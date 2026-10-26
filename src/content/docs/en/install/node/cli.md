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
