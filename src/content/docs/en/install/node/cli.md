---
title: CLI and updates
description: gowave-node commands, updating the node and the Xray core.
sidebar:
  order: 3
---

## Commands

| Command | What it does |
| :--- | :--- |
| `gowave-node status` | Status of the service, daemon, and Xray core |
| `gowave-node status --wait-running` | Wait for the management daemon to start (up to 30 s) |
| `gowave-node status --wait-ready` | Wait until the node receives configuration and Xray starts (up to 120 s) |
| `gowave-node logs -n 100 -f` | Node service log |
| `gowave-node xlogs -n 100 -f` | Xray core log (or standalone `xlogs` command) |
| `gowave-node restart` | Restart service |
| `gowave-node update` | Interactive selection and node update |
| `gowave-node update -y` | Update the node to the latest stable release |
| `gowave-node update --version v1.1.5 -y` | Install a specific node version |
| `gowave-node core install` | Interactive selection and installation of Xray core |
| `gowave-node core install -y` | Install the latest stable Xray |
| `gowave-node core install --version v26.7.28 -y` | Install a specific Xray version |
| `gowave-node core install --repo owner/repo --version v1.0.0 -y` | Install a custom Xray core from another repository |
| `gowave-node core update` | Update Xray core to the latest stable release |
| `gowave-node core reset` | Restore the default managed core (`rw-core`) |
| `gowave-node version` | Print current node version |

Run commands as the service user, usually `root` (or via `sudo`): the CLI communicates with the daemon through a private discovery file in `/run/gowave-node` (or the path set in `GOWAVE_NODE_RUNTIME_DIR`). Installs moved from the old name also keep the `remnanode` and `remnanode-go` commands.

The installer also creates an `xlogs` system symlink, allowing direct log viewing: `xlogs -n 100 -f`.

## Status and logs

- `gowave-node status` checks the accessibility of the management socket, the systemd unit (or init system) state, the path and version of the detected Xray core, and the node version itself.
- In `gowave-node logs` (alias: `gowave-node nodelogs`) and `gowave-node xlogs`, `-n` (or `--lines`) configures the number of lines displayed (defaults to 100), and `-f` (`--follow`) streams new entries. The node log is served directly from an in-memory ring buffer.

## Node updates

Running `gowave-node update` without arguments shows available GitHub releases and prompts you to select a version:

```bash
gowave-node update
```

Available flags:

- `-y`, `--yes` - apply update without prompting;
- `--channel <release|prerelease>` - select release channel (defaults to `release`);
- `--version <tag>`, `-v <tag>` - install an explicit version;
- `--repo <owner/repo>`, `-r <owner/repo>` - GitHub repository (defaults to `aaaSaZaN/gowave-node`).

Updates are transactional: the previous binary is saved as a backup (`.previous`), the new binary is validated prior to replacement, and a restart failure automatically rolls back to the prior version.

## Managing the Xray core

The `core` command manages the Xray binary and geodata files:

- `gowave-node core install` fetches releases from `XTLS/Xray-core`, verifies the binary, and downloads updated geodata (`geosite.dat`, `geoip.dat`) to the asset directory.
- Flags `--version <tag>` and `--repo <repo>` allow selecting a specific release or an alternative core fork.
- `gowave-node core reset` clears custom core overrides and restores the standard managed `rw-core`.

### Installing a custom core

To install a core from a third-party GitHub repository, pass the repository and version tag:

```bash
gowave-node core install --repo <owner/repo> --version <tag> -y
```

Examples:

```bash
# Install a specific official release
gowave-node core install --repo XTLS/Xray-core --version v26.7.28 -y

# Install a custom fork or build
gowave-node core install --repo owner/custom-xray --version v1.0.0 -y
```

Requirements for the custom repository:

- GitHub Releases in the target repository must include compiled archives (`.zip`) or binaries matching your system architecture (for example, `Xray-linux-64.zip` or arm64 archives).
- The binary must support standard Xray startup parameters. The node validates the binary with a dry-run test before replacing `rw-core`.

### What happens during node updates

The `gowave-node update` command updates only the node daemon binary itself.

The installed Xray core is neither overwritten nor reset. If you installed a custom core fork via `core install` or specified a core URL, the node keeps using it after being updated and restarted. To switch back to the official default core, run `gowave-node core reset`.

## Updating from the panel

In the GoWave panel:

- **Xray Core**: click the core version in the node card to choose a stable release, pre-release, or enter a direct HTTPS URL to a core binary or archive.
  Example direct link:
  `https://github.com/XTLS/Xray-core/releases/download/v26.7.28/Xray-linux-64.zip`
  or a direct link to a raw binary:
  `https://example.com/builds/xray-linux-64`
- **GoWave Node**: the node version is managed under the GoWave Node version selector. The release list is fetched from [gowave-node](https://github.com/aaaSaZaN/gowave-node). The panel sends an update command to the node, which performs a safe transactional update with automatic readiness verification.

Panel updates need systemd. On Entware, update the node with `gowave-node update`. On an s6-only host a panel update works only with an external restart supervisor; without one the node rejects the request and keeps the current binary.
