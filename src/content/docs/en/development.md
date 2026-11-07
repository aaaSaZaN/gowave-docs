---
title: Building from source
description: Building GoWave and its Docker image yourself.
sidebar:
  order: 1
---

Repository: [aaaSaZaN/gowave](https://github.com/aaaSaZaN/gowave).

- `backend-go/` - the Go backend (module `gowave`).
- `frontend/` - the web interface on React, TypeScript and Vite.

## Binaries

Use the Bun version from `frontend/package.json` (`packageManager`) and the Go version from `backend-go/go.mod`.

```bash
git clone https://github.com/aaaSaZaN/gowave.git
cd gowave

# Web interface
cd frontend
bun install --frozen-lockfile
bun run editor:download
bun run build
bun run editor:compress
cd ..

# Backend
cd backend-go
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o gowave-linux-amd64 ./cmd/server
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -ldflags="-s -w" -o gowave-linux-arm64 ./cmd/server
```

The web interface is not embedded in the binary: the panel looks for `frontend/dist` next to its working directory.

Without these flags the binary reports the version written in the source and the stable channel. Releases set the version, channel and commit with `-ldflags`:

```bash
go build -trimpath -ldflags="-s -w \
  -X gowave/internal/system.AppVersion=v1.2.3 \
  -X gowave/internal/system.Channel=stable \
  -X gowave/internal/system.CommitSha=$(git rev-parse HEAD)" \
  -o gowave-linux-amd64 ./cmd/server
```

## Docker image

Build the image from source instead of pulling from `ghcr.io`:

```bash
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

The image builds in three stages: the web interface on `oven/bun` (once, since it does not depend on the architecture), the backend on `golang` with cross-compilation instead of QEMU, and the final image on `alpine`. The `VERSION`, `CHANNEL` (`stable` or `dev`) and `COMMIT_SHA` build arguments set the version.

## Publishing builds

- A push to `main`: after CI, the `dev.yml` workflow rebuilds the `dev` pre-release and the `:dev` and `:dev-<sha>` images. Pushes that change only Markdown files do not trigger it.
- A `v1.2.3` tag: the `release.yml` workflow runs CI and publishes the stable release and the `:1.2.3` and `:latest` images. A tag with a hyphen (`v1.2.3-beta.1`) becomes a pre-release and does not move `latest`.

## Checks

```bash
cd backend-go
go vet ./...
go test -race -count=1 ./...
```

Tests use in-memory SQLite by default. For PostgreSQL:

```bash
GOWAVE_TEST_POSTGRES='postgres://gowave:gowave@localhost:5432/gowave_test?sslmode=disable' go test -count=1 ./...
```
