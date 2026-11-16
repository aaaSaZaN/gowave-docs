---
title: Configuration
description: GoWave Node environment variables.
sidebar:
  order: 2
---

Settings are read from `.env` next to the binary or from `/opt/gowave-node/.env` (for migrated setups, `/opt/remnanode/.env` is also supported). Variables set in the process environment take precedence. The installer writes `SECRET_KEY` and `NODE_PORT`; the rest rarely needs changing.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *required* | Key from the node settings in the panel: certificates and signing for the connection |
| `NODE_PORT` | `3000` | Management port (TLS 1.3, mTLS and RS256 JWT). Must match the node port in the panel |
| `XRAY_CORE_PATH` | found next to it or on the system | Path to the Xray core binary |
| `XRAY_LOCATION_ASSET` | the core's directory | Geodata directory (`geoip.dat`, `geosite.dat`) |
| `ASN_INDEX_PATH` | `/usr/local/share/asn/asn-prefixes.zip` | ASN index for plugin lists |
| `SNI_VERIFICATION` | `false` | Require the panel-issued SNI even with valid mTLS |
| `NFTABLES_LOGGING` | `true` | Kernel firewall logging |
| `NFTABLES_ACCEPT_REPLY_TRAFFIC` | `false` | Do not block reply traffic of established connections |
| `DISABLE_HASHED_SET_CHECK` | `false` | Restart the core on every configuration sync |
| `GOWAVE_NODE_RUNTIME_DIR` | `/run/gowave-node` | Private configuration and CLI directory (on Entware: `/tmp/gowave-node`). The installer translates the legacy `REMNANODE_RUNTIME_DIR` name |
| `XTLS_API_SOCKET_PATH` | `/run/gowave-node/xray.sock` | Xray gRPC socket |
| `INTERNAL_REST_TOKEN` | random | Internal HTTP token, normally unset |
| `INTERNAL_SOCKET_PATH` | random | Internal configuration and webhook socket |
| `S6_COMMAND_DIR`, `XRAY_S6_SERVICE_DIR` | `/command`, `/run/service/xray` | For running Xray under s6, as in the original container |

The runtime directory is created with mode `0700`, and the configuration and CLI files in it with `0600`. The Xray configuration is kept only there and is never copied to `/etc/xray/config.json`. Internal TCP endpoints must use a loopback address.

## Plugins

Supported: ingress and egress filters, ASN lists, torrent detection with reports to the panel, connection termination and post-start webhooks. Filters need `nft`, `ss` and `CAP_NET_ADMIN`; without them the node reports to the panel that the rules could not be applied.

## Geocheck

A geocheck started from the panel runs `/usr/local/bin/geocheck`. If it is missing, the node downloads a pinned geocheck release for the run and removes it afterwards. Builds exist only for `amd64` and `arm64`; on other architectures the check returns an error.

## Custom core

The node configuration can name a custom Xray core (`xrayConfig.geodata.core`: URL and SHA-256) and extra data files (`geodata.assets`). A custom core is first validated against the current configuration and only then switched on.

The core can also be installed via CLI (`gowave-node core install --repo <owner/repo> --version <tag>`) or via direct HTTPS download URL in the GoWave web panel. When running `gowave-node update`, any custom core is preserved and remains active. Running `gowave-node core reset` reverts to the default managed core.
