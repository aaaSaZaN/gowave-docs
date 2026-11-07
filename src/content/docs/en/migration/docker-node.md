---
title: Docker node to Go node
description: Moving a node from the remnawave/node image to GoWave Node.
sidebar:
  order: 5
---

If a node runs in Docker on the `remnawave/node` image, the same installer moves it to [GoWave Node](../../install/node/install/) (as root on the node server):

```bash
sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave-node/main/install.sh)"
```

The installer finds the container and carries its environment (`SECRET_KEY`, `NODE_PORT` and the rest) into the Go node's `.env`, so nothing changes in the panel.

Step by step:

1. While the container is running, the installer reads its current Xray configuration and checks that the certificate and key files it references (`certificateFile`, `keyFile`, `dhFile`) are readable on the host. If a file exists only inside the container, the installer stops and leaves Docker alone. Copy or mount such files onto the host and run the command again.
2. It downloads and verifies the release and installs the `gowave-node` service.
3. It turns off the container's restart policy, stops the container and starts the Go node.
4. It waits up to two minutes for the node to get its configuration from the panel and start Xray. If that does not happen, the container comes back with its previous restart policy.

The container itself is not removed; it stays stopped in case you want to roll back by hand. Once the Go node has run without trouble for a while, remove it yourself.

If the server has both a Docker node and an old native `remnanode` service, the installer does not guess and asks you to keep only one of them first.
