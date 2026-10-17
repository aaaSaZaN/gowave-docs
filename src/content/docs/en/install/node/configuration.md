---
title: Configuration
description: Go node environment variables.
sidebar:
  order: 2
---

Settings are read from `.env` next to the binary or from `/opt/remnanode/.env`. Variables set in the process environment take precedence. The installer writes `SECRET_KEY` and `NODE_PORT`; the rest rarely needs changing.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *required* | Key from the node settings in the panel: certificates and signing for the connection |
| `NODE_PORT` | `3000` | Management port (TLS 1.3, mTLS and RS256 JWT). Must match the node port in the panel |
| `XRAY_CORE_PATH` | found next to it or on the system | Path to the Xray core |
| `XRAY_LOCATION_ASSET` | the core's directory | Geodata directory |
| `ASN_INDEX_PATH` | `/usr/local/share/asn/asn-prefixes.zip` | ASN index for plugin lists |
| `SNI_VERIFICATION` | `false` | Require the panel-issued SNI even with valid mTLS |
| `NFTABLES_LOGGING` | `true` | Kernel firewall logging |
| `NFTABLES_ACCEPT_REPLY_TRAFFIC` | `false` | Do not block reply traffic of established connections |
| `DISABLE_HASHED_SET_CHECK` | `false` | Restart the core on every configuration sync |
| `REMNANODE_RUNTIME_DIR` | `/run/remnanode` | Private configuration and CLI directory |
| `XTLS_API_SOCKET_PATH` | `/run/remnanode/xray.sock` | Xray gRPC socket |
| `INTERNAL_REST_TOKEN` | random | Internal HTTP token, normally unset |
| `INTERNAL_SOCKET_PATH` | random | Internal configuration and webhook socket |
| `S6_COMMAND_DIR`, `XRAY_S6_SERVICE_DIR` | `/command`, `/run/service/xray` | For running Xray under s6, as in the original container |

The runtime directory must belong to the service user with mode `0700`. The Xray configuration is kept only there and is never copied to `/etc/xray/config.json`.

## Plugins

Supported: ingress and egress filters, ASN lists, torrent detection with reports to the panel, connection termination and post-start webhooks. Filters need `nft`, `ss` and `CAP_NET_ADMIN`; without them the node reports to the panel that the rules could not be applied.

## Custom core

The node configuration can name a custom Xray core (`xrayConfig.geodata.core`: URL and SHA-256) and extra data files (`geodata.assets`). A custom core is first validated against the current configuration and only then switched on. `remnanode core reset` brings back the standard one.
