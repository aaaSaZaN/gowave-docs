---
title: Installation
description: Installing Gowave Node (gowave-node) with one command.
sidebar:
  order: 1
---

Gowave Node ([gowave-node](https://github.com/aaaSaZaN/gowave-node)) manages the Xray core on the server carrying user traffic. It is a fast and lightweight Go implementation of the node: compatible with the Remnawave Node 3.4.2 protocol, it connects to both Gowave and the original Remnawave panel. Xray runs as a separate process; Node.js and Docker are not needed.

The project was previously named remnanode-go, and the command was `remnanode`. The installer migrates existing installations automatically.

## Requirements

- Linux. Architectures: `amd64`, `386`, `arm64`, `armv7`, `armv6`, `armv5`, `riscv64`, `mips`, `mipsle`, `mips64`, `mips64le`. Server verification passes on `amd64` and `arm64`; other router builds are not certified.
- Service manager: systemd, OpenRC (Alpine), procd (OpenWrt), or Entware (Keenetic and other opkg systems).
- `curl` or `wget`, and one of `sha256sum`, `shasum`, `openssl`.
- Root access.
- Traffic filters in plugins require `nft`, `ss` (iproute2), and `CAP_NET_ADMIN`.

## Install from the panel

When adding a node, the panel displays a ready-to-run command with the `SECRET_KEY` and node port prefilled. Copy and run it on the node server.

If the panel is hosted on the same server, the [Gowave installer](../../installer/#local-node) can deploy the node automatically.

## Quick script installation

1. Add the node in the panel and copy its `SECRET_KEY` from the node configuration drawer.
2. On the node server, run:

   ```bash
   sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave-node/main/install.sh)"
   ```

   Without `curl`, use `sudo sh -c "$(wget -qO- https://raw.githubusercontent.com/aaaSaZaN/gowave-node/main/install.sh)"`.

3. The installer prompts for `SECRET_KEY` and `NODE_PORT` (default: `3000`). The port must match the node settings in the panel.

Non-interactive automated installation (e.g. for provisioning scripts):

```bash
sudo SECRET_KEY=... NODE_PORT=2222 sh -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave-node/main/install.sh)"
```

If the requested port is already in use, the installer halts before making any modifications. A fresh node is ready once the management daemon responds (within 30 seconds), so panel setup can proceed immediately. During updates or migrations, the script waits up to 2 minutes for Xray readiness and rolls back if startup fails.

### Installer options

| Variable | Description |
| :--- | :--- |
| `SECRET_KEY` | Node secret key from panel settings. Used only on fresh unconfigured installs |
| `NODE_PORT` | Management port, defaults to `3000`. Must match the node configuration in the panel |
| `GOWAVE_NODE_VERSION` | Specific release tag instead of latest (e.g. `v1.1.5` or a pre-release). The script aborts if the tag does not exist |
| `GOWAVE_NODE_INIT` | Force specific init system detection: `systemd`, `openrc`, `procd`, or `entware` |

Legacy environment variables with the `REMNANODE_` prefix are accepted for backward compatibility; `GOWAVE_NODE_` variables take precedence.

## Installing custom Xray binaries

By default, `gowave-node` installs and maintains the standard Xray core (`rw-core`). You can also install custom builds, forks, or explicit releases via CLI or through the Gowave web panel.

### Via node CLI

The `gowave-node core install` command downloads releases from any public GitHub repository:

```bash
gowave-node core install --repo <owner/repo> --version <tag> -y
```

Examples:

```bash
# Install a specific release from the official XTLS/Xray-core repo
gowave-node core install --repo XTLS/Xray-core --version v26.7.28 -y

# Install a custom fork or community build
gowave-node core install --repo owner/custom-xray --version v1.0.0 -y
```

Repository requirements:
- GitHub Releases in the target repository must include compiled `.zip` archives or binaries matching your server architecture (e.g. `Xray-linux-64.zip` or arm64 archives).
- The node extracts the binary, verifies execution against the current configuration, and activates the core only after passing validation.

### Via Gowave web panel

In the Gowave web interface:
1. Open the node card and click the current **Xray Core** version.
2. Select a release or paste a direct HTTPS download URL to an archive or binary.

Example direct links:
```text
https://github.com/XTLS/Xray-core/releases/download/v26.7.28/Xray-linux-64.zip
```
Or a direct link to a raw binary build:
```text
https://example.com/builds/xray-linux-64
```

The panel instructs the node to download the asset over HTTPS, validate it, and restart the node service to activate the core. Active connections may be briefly interrupted. If `CUSTOM_CORE_URL` is set, the node manages the core locally and Gowave disables this action.

### Resetting to the default core

If `CUSTOM_CORE_URL` is set, remove it from `.env` and restart Gowave Node to return control to the panel. To reset a CLI-installed or panel-installed core to the default (`rw-core`), run:

```bash
gowave-node core reset
```

This restores the saved stock `rw-core` binary and restarts the node.

### Node update persistence

By default, `gowave-node update` updates only the node daemon. With `--with-core`, it runs `gowave-node core update` after updating the node.

Your active Xray core (including custom builds installed with `--repo` or via direct URLs) is preserved when updating the node without `--with-core`.

## Connecting to the panel

The node does not initiate outbound connections to the panel. The `gowave-node` daemon listens on `NODE_PORT` (default 3000), and the panel connects to `https://<node-ip>:<node-port>`.

The connection is secured with mutual TLS (mTLS over TLS 1.3) and RS256 JWT tokens. Certificates and keys are packed inside `SECRET_KEY`.

### Remnawave compatibility

The node implements the Remnawave Node API protocol version 3.4.2:
- Status and version checks return protocol version `3.4.2` to pass Remnawave's compatibility check.
- Users synchronize sequentially: the panel issues separate requests for each user (`add-user` and `remove-user`).

### Gowave advantages

When paired with Gowave, connection efficiency is increased:
- The panel sends the `X-Better-One: true` header. The node reports its true release version and the `go` runtime type. The panel shows exact version details and allows one-click updates.
- Bulk synchronization: Gowave syncs users in batches of up to 1,000 users per request via `add-users` and `remove-users`, preventing queue saturation on node restarts.
- Decoupled polling: health checks run every 15 seconds (up to 32 concurrent checks), while stats polling runs every 5 seconds, evenly distributed over the interval. This protects the database and network from traffic spikes. If recording usage temporarily fails, the node retries on the next poll without lost bytes.

## Installed components

- Installation directory: `/opt/gowave-node`.
- Systemd service: `gowave-node.service` (runs as `root` because Xray requires access to sockets in `/dev/shm`, external certificates, and low ports below 1024).
- ASN prefix index for plugins: `/usr/local/share/asn/asn-prefixes.zip`.
- Symlinks in `/usr/local/bin`: `gowave-node` and `xlogs`.

## Entware (routers)

On Entware, the installer creates `/opt/etc/init.d/S99gowave-node`. `rc.unslung` launches it at boot, and the script restarts the node 3 seconds after an unexpected exit. Files reside in `/opt`, commands in `/opt/bin`, and runtime data in `/tmp/gowave-node`.

Key points:
- Node output bypasses the router system log; read it with `gowave-node logs`.
- Panel-triggered updates require systemd; on Entware, update via CLI with `gowave-node update`.
- Open `NODE_PORT` and inbound Xray ports in the router firewall on the WAN interface.

## Migrating from legacy remnanode

If the server previously ran `remnanode`, the installer transitions to `gowave-node` automatically:
- The installation directory is retained (e.g. `/opt/remnanode`) so custom core and certificate paths remain valid.
- Credentials, ports, and configuration from `.env` are preserved and translated to new variable names.
- `remnanode` and `remnanode-go` commands remain as symlinks to `gowave-node`.
- The old service is disabled only after the new binary is verified.

If the previous node used a non-standard location, define `GOWAVE_NODE_LEGACY_INSTALL_DIR`.

## Manual installation without the script

Binaries (`gowave-node-linux-<arch>`) and `checksums.txt` are available on the [gowave-node releases](https://github.com/aaaSaZaN/gowave-node/releases) page.

1. Place the binary at `/opt/gowave-node/gowave-node` and grant execute permissions: `chmod +x /opt/gowave-node/gowave-node`.
2. Create `/opt/gowave-node/.env` as described in [configuration](../configuration/).
3. Create the systemd service file `/etc/systemd/system/gowave-node.service`:

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

4. Install the Xray core and configure system symlinks:

```bash
/opt/gowave-node/gowave-node core install -y
ln -sfn /opt/gowave-node/gowave-node /usr/local/bin/gowave-node
ln -sfn /opt/gowave-node/gowave-node /usr/local/bin/xlogs
systemctl daemon-reload
systemctl enable --now gowave-node
```
