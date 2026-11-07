---
title: Updating
description: Updating GoWave on systemd and in Docker, stable and dev channels.
sidebar:
  order: 7
---

The panel checks GitHub releases and shows in the header when a new version is out. Click the version to open **Build Info**: it shows when the last check ran, and **Check now** asks GitHub again instead of answering from the cache.

## Stable and dev channels

| | Stable | Dev |
| :--- | :--- | :--- |
| Built from | `v*` tags | Every commit to `main` that passes CI |
| Binaries | [Latest release](https://github.com/aaaSaZaN/gowave/releases/latest) | The [`dev`](https://github.com/aaaSaZaN/gowave/releases/tag/dev) pre-release, rebuilt on every commit |
| Docker | `ghcr.io/aaasazan/gowave:latest`, `:1.2.3` | `ghcr.io/aaasazan/gowave:dev`, `:dev-<sha>` |
| Version | `v1.2.3` | `dev-<sha>` |

Dev builds may be unstable, but fixes land there right away. A panel on dev shows its version in red. Stable updates and the `latest` tag never pick up dev builds. Pre-releases tagged like `v1.2.0-beta.1` are not offered either; install them by hand with [`--version`](../installer/#command-line-options).

Pick the channel in **Build Info** with the **Stable (releases)** / **Dev (every commit)** switch, or in the installer. Later updates stay on the chosen channel.

:::caution[Back up first]
A stable release can be older than the dev build you are leaving, and database changes made by the dev build are not rolled back. Back up the database before you switch channels.
:::

## Systemd and SQLite

Click **Update panel** (or **Switch to dev** / **Switch to stable** when changing channels) in **Build Info**. The panel runs without root and cannot replace its own files, so it only leaves a request in `/run/gowave`. A separate root service, `gowave-update`, carries it out:

1. downloads the binary, the web interface and `SHA256SUMS` of the chosen channel;
2. checks the checksums;
3. installs the web interface and replaces the binary, keeping the previous one as `gowave-server.bak`;
4. reapplies the service restrictions and restarts the panel.

The window shows each step, the download progress and a log. If the update fails, the error shows up there and the panel keeps running the old version. It usually takes under a minute. The full log on the server:

```bash
journalctl -u gowave-update.service
```

If the new version does not work out, you can put the previous binary back by hand:

```bash
cp /opt/gowave/gowave-server.bak /opt/gowave/gowave-server && systemctl restart gowave
```

On installs made before the update service existed, the panel shows the installer command instead of the button. After one update with the installer, the button works.

Or run the installer again. Its menu has an update option and asks for the channel, and it reapplies the service restrictions along the way:

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/gowave/main/install.sh)"
```

For updates without prompts, for example from cron or Ansible, use the [`--update`](../installer/#command-line-options) option.

## Docker

There is no button in Docker. The panel shows the command to run on the server instead:

```bash
cd /opt/gowave-docker && docker compose pull && docker compose up -d
```

In Docker the channel is the image in `GOWAVE_IMAGE` in `.env`. When you switch channels in **Build Info**, the panel shows a command that replaces it:

```bash
cd /opt/gowave-docker
sed -i '/^GOWAVE_IMAGE=/d' .env && echo 'GOWAVE_IMAGE=ghcr.io/aaasazan/gowave:dev' >> .env
docker compose pull && docker compose up -d
```

Use `:latest` instead of `:dev` to go back to stable. The project path in the hint comes from `GOWAVE_COMPOSE_DIR`.

A container cannot replace its own image. Something outside has to do it, and that requires the Docker socket, which means root on the host. Giving that to a web panel would turn a panel compromise into a server compromise, so Docker updates stay a regular command.

## Version

```bash
gowave --version
```

In Docker: `docker exec gowave /app/gowave --version`.
