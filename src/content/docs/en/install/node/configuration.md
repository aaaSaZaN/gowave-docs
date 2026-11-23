---
title: Configuration
description: Gowave Node environment variables.
sidebar:
  order: 2
---

Settings are read from `.env` next to the binary or from `/opt/gowave-node/.env` (for migrated setups, `/opt/remnanode/.env` is also supported). Variables set in the process environment take precedence. The installer writes `SECRET_KEY` and `NODE_PORT`; the rest rarely needs changing.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *required* | Key from the node settings in the panel: certificates and signing for the connection |
| `NODE_PORT` | `3000` | Management port (TLS 1.3, mTLS and RS256 JWT). Must match the node port in the panel |
| `XRAY_CORE_PATH` | found next to it or on the system | Path to the Xray core binary |
| `CUSTOM_CORE_URL` | — | Direct HTTPS URL for a local Xray core |
| `CUSTOM_CORE_SHA256` | — | Optional SHA-256 of the downloaded file |
| `XRAY_LOCATION_ASSET` | the core's directory | Geodata directory (`geoip.dat`, `geosite.dat`) |
| `GEOIP_URL` | — | HTTPS URL for `geoip.dat` |
| `GEOSITE_URL` | — | HTTPS URL for `geosite.dat` |
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

The core can also be installed via CLI (`gowave-node core install --repo <owner/repo> --version <tag>`) or via direct HTTPS download URL in the Gowave web panel. When running `gowave-node update`, any custom core is preserved and remains active. With `CUSTOM_CORE_URL` unset, `gowave-node core reset` restores the default managed core.

### Local core from `.env`

Set `CUSTOM_CORE_URL` to a direct HTTPS URL for an Xray-compatible binary or a ZIP, TAR.GZ, or TGZ archive built for the node's OS and architecture. Optionally set `CUSTOM_CORE_SHA256` to the 64-character hexadecimal SHA-256 of the downloaded file (the archive itself if you use one).

Restart Gowave Node after adding the variable. On the next Xray start requested by the panel, the node downloads the core if needed and keeps it as `rw-core.local` next to the node executable. This core takes precedence over the core selected in the panel. The Gowave node card shows that the core is managed locally and disables core installation from the panel. Updating Gowave Node itself remains available.

Run `gowave-node core update` to replace an existing `rw-core.local`, including after changing the URL or checksum. To return control to the panel, remove `CUSTOM_CORE_URL` and restart Gowave Node.

## Custom geodata

Set `GEOIP_URL` and/or `GEOSITE_URL` to direct HTTPS URLs for the corresponding `.dat` files. Use `XRAY_LOCATION_ASSET` to set the resource directory explicitly. At startup the node downloads missing or empty files from the configured sources and keeps existing nonempty files. Each configured URL takes precedence over a panel asset with the same filename.

After changing the URL or to refresh the files, run `gowave-node geodata update`, then restart Gowave Node so Xray loads them. The command downloads all configured files before replacing any of them.
