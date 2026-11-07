---
title: Installation
description: Installing GoWave Node (gowave-node) with one command.
sidebar:
  order: 1
---

GoWave Node ([gowave-node](https://github.com/aaaSaZaN/gowave-node)) manages the Xray core on the server that carries user traffic. It is a Go implementation of the Remnawave node. The panel protocol is compatible with Remnawave Node 3.4.2, so the node connects to both GoWave and the original Remnawave panel. Xray runs as a separate process; Node.js and Docker are not needed.

The project used to be called remnanode-go, with a `remnanode` command. The installer moves old installs to the new name by itself, see [below](#moving-from-an-old-remnanode-install).

## Requirements

- Linux. Architectures: `amd64`, `386`, `arm64`, `armv7`, `armv6`, `armv5`, `riscv64`, `mips`, `mipsle`, `mips64`, `mips64le`. Server tests run on `amd64` and `arm64`; router builds are not certified.
- Service manager: systemd, OpenRC (Alpine), procd (OpenWrt) or Entware init.d (Keenetic and other opkg systems).
- `curl` or `wget`, and one of `sha256sum`, `shasum`, `openssl`.
- Root access.
- Traffic filters in plugins need `nft`, `ss` (iproute2) and `CAP_NET_ADMIN`.

## Install from the panel

When you add a node, the panel shows a ready command with the `SECRET_KEY` and the node port filled in. Copy it with the button and run it on the node server.

If the panel runs on the same server, the [GoWave installer](../../installer/#local-node) can install the node as well.

## Install by hand

1. Add the node in the panel and copy its `SECRET_KEY` from the node settings.
2. On the node server run:

   ```bash
   sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave-node/main/install.sh)"
   ```

   Without `curl`, use `sudo sh -c "$(wget -qO- <same URL>)"`.

3. The installer asks for `SECRET_KEY`. The management port defaults to `3000` and must match the node port in the panel. Pass another port in `NODE_PORT`.

Without prompts, for example from a script:

```bash
sudo SECRET_KEY=... NODE_PORT=2222 sh -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave-node/main/install.sh)"
```

If another program holds the port, the installer stops before it changes anything. A fresh install is done once the management service answers (up to 30 seconds), so you can configure the node in the panel right after. Updates and migrations wait up to two minutes for Xray to start and bring back the previous service if it does not.

The same command updates an installed node and moves a node out of Docker, see [From the Docker node to the Go node](../../../migration/docker-node/).

### Installer options

| Variable | Sets |
| :--- | :--- |
| `SECRET_KEY` | Key from the node settings. Used only when the node is not configured yet |
| `NODE_PORT` | Management port, `3000` by default. Also only for a node that is not configured yet |
| `GOWAVE_NODE_VERSION` | A release tag instead of the latest, for example `v1.0.6-rc.1` to try a candidate. If the tag does not exist, the installer changes nothing |
| `GOWAVE_NODE_INIT` | Service manager when detection gets it wrong: `systemd`, `openrc`, `procd` or `entware` |

The old `REMNANODE_` variables are still accepted; the `GOWAVE_NODE_` ones win.

## What gets installed

A fresh install lives in `/opt/gowave-node`. The service is `gowave-node` and runs as root, like the Docker node: Xray has to reach whatever the panel configuration points to, such as sockets in `/dev/shm` shared with nginx, other services' certificates and ports below 1024. If you want isolation, add your own systemd override.

The installer also puts the ASN index for plugins in `/usr/local/share/asn/asn-prefixes.zip`.

## Entware

On Entware the installer writes `/opt/etc/init.d/S99gowave-node`. `rc.unslung` starts it at boot, and the script brings the node back 3 seconds after it exits. Files live in `/opt`, commands in `/opt/bin`, and the runtime directory is `/tmp/gowave-node`.

Things to know:

- node output does not go to the system log; read it with `gowave-node logs`;
- updates from the panel need systemd, so update with `gowave-node update`;
- open `NODE_PORT` and the Xray inbound ports for the WAN interface in the router firewall.

## Moving from an old remnanode install

If the server runs the node under its old name (`remnanode`), the installer switches it to the `gowave-node` service automatically:

- the install directory stays the same, for example `/opt/remnanode`, so certificate paths and a custom core keep working;
- the secret, port and other `.env` settings are kept, and old variable names are translated;
- `remnanode` and `remnanode-go` stay as links to `gowave-node`;
- the old service is turned off only after the new release is downloaded and verified. If the switch fails, the previous service and `.env` come back.

If the old node lived in a non-standard directory, set `GOWAVE_NODE_LEGACY_INSTALL_DIR` (systemd finds it from the service's `WorkingDirectory`). Do not change the install directory during the move. Review your own unit overrides and s6 definitions separately; the installer does not rename them.

## Manual install without the installer

`gowave-node-linux-<architecture>` binaries, `checksums.txt` and `asn-prefixes.zip` are in the [gowave-node releases](https://github.com/aaaSaZaN/gowave-node/releases). Put the binary in `/opt/gowave-node`, create `.env` as described in [configuration](../configuration/) and a systemd service:

```ini
[Unit]
Description=gowave-node
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/gowave-node
ExecStart=/opt/gowave-node/gowave-node
RuntimeDirectory=gowave-node
RuntimeDirectoryMode=0700
UMask=0077
Restart=always
RestartSec=3
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

Then install the core and start the service:

```bash
/opt/gowave-node/gowave-node core install -y
systemctl enable --now gowave-node
```

The binary does not create links in `PATH` by itself. To run `gowave-node` from anywhere, add one: `ln -s /opt/gowave-node/gowave-node /usr/local/bin/gowave-node`.
