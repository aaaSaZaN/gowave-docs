---
title: Installation
description: Installing the Go node with one command.
sidebar:
  order: 1
---

The Go node ([remnanode-go](https://github.com/aaaSaZaN/remnanode-go)) manages the Xray core on the server that carries user traffic. It is a Go implementation of the Remnawave node, compatible with Remnawave Node 3.4.2, and connects to both GoWave and the original Remnawave panel. Xray runs as a separate process; Node.js and Docker are not needed.

## Requirements

- Linux. Architectures: `amd64`, `386`, `arm64`, `armv7`, `armv6`, `armv5`, `riscv64`, `mips`, `mipsle`, `mips64`, `mips64le`. Server tests run on `amd64` and `arm64`; the other builds for routers are not certified.
- Service manager: systemd, OpenRC (Alpine) or procd (OpenWrt).
- `curl` or `wget`, and one of `sha256sum`, `shasum`, `openssl`.
- Root access.
- Traffic filters in plugins need `nft`, `ss` (iproute2) and `CAP_NET_ADMIN`.

## Install

1. Add the node in the panel and copy its `SECRET_KEY` from the node settings.
2. On the node server run:

   ```bash
   sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/remnanode-go/main/install.sh)"
   ```

   Without `curl`, use `sudo sh -c "$(wget -qO- <same URL>)"`.

3. The installer asks for `SECRET_KEY` and `NODE_PORT` (default `3000`). The port must match the node port in the panel.

Without prompts, for example from a script:

```bash
sudo SECRET_KEY=... NODE_PORT=2222 sh -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/remnanode-go/main/install.sh)"
```

## Manual installation

`remnanode-linux-<architecture>` binaries and `checksums.txt` are in the [remnanode-go releases](https://github.com/aaaSaZaN/remnanode-go/releases). Put the binary in `/opt/remnanode`, create `.env` as described in [configuration](../configuration/) and a systemd service:

```ini
[Unit]
Description=Remnanode (Go)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/remnanode
ExecStart=/opt/remnanode/remnanode
RuntimeDirectory=remnanode
RuntimeDirectoryMode=0700
UMask=0077
Restart=on-failure
RestartSec=3
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

Then install the core: `/opt/remnanode/remnanode core install -y`.
