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
