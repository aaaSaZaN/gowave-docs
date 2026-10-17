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

```bash
git clone https://github.com/aaaSaZaN/gowave.git
cd gowave

# Web interface
pnpm --prefix frontend install --frozen-lockfile
pnpm --prefix frontend build

# Backend
cd backend-go
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o gowave-linux-amd64 ./cmd/server
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -ldflags="-s -w" -o gowave-linux-arm64 ./cmd/server
```

The web interface is not embedded in the binary: the panel looks for `frontend/dist` next to its working directory.

## Docker image

Build the image from source instead of pulling from `ghcr.io`:

```bash
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

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
