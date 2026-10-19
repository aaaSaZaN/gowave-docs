---
title: Docker node to Go node
description: Moving a node from the remnawave/node image to the Go node.
sidebar:
  order: 4
---

If a node runs in Docker on the `remnawave/node` image, the same installer moves it to the Go node (as root on the node server):

```bash
sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/remnanode-go/main/install.sh)"
```

The installer finds the container and carries its environment (`SECRET_KEY`, `NODE_PORT` and the rest) into the Go node's `.env`, so nothing changes in the panel.

## Checks before Docker is stopped

- all node and core files are downloaded and verified against checksums;
- the TLS files referenced by the running configuration exist on the host. Paths from the container must exist at the same locations on the server.

Until every check passes, the container keeps running.

## The switch

The installer stops the container, starts the Go node and waits up to 120 seconds for the panel to send the configuration and for Xray to become ready. Existing connections drop during the switch. The downtime depends on how fast the panel syncs the node; the installer measures it and prints it.

If the Go node does not come up, the installer brings the container back with its restart policy. The old container is kept even after a successful move; remove it by hand when you no longer need it.
