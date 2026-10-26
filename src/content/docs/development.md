---
title: Сборка из исходников
description: Как собрать GoWave и Docker-образ самостоятельно.
sidebar:
  order: 1
---

Репозиторий: [aaaSaZaN/gowave](https://github.com/aaaSaZaN/gowave).

- `backend-go/` - бэкенд на Go (модуль `gowave`).
- `frontend/` - веб-интерфейс на React, TypeScript и Vite.

## Бинарники

Используйте версию Bun из `frontend/package.json` (`packageManager`) и версию Go из `backend-go/go.mod`.

```bash
git clone https://github.com/aaaSaZaN/gowave.git
cd gowave

# Веб-интерфейс
cd frontend
bun install --frozen-lockfile
bun run editor:download
bun run build
bun run editor:compress
cd ..

# Бэкенд
cd backend-go
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o gowave-linux-amd64 ./cmd/server
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -ldflags="-s -w" -o gowave-linux-arm64 ./cmd/server
```

Веб-интерфейс не встраивается в бинарник: панель ищет `frontend/dist` рядом с рабочей папкой.

## Docker-образ

Собрать образ из исходников вместо `ghcr.io`:

```bash
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

## Проверки

```bash
cd backend-go
go vet ./...
go test -race -count=1 ./...
```

Тесты по умолчанию работают на SQLite в памяти. Для PostgreSQL:

```bash
GOWAVE_TEST_POSTGRES='postgres://gowave:gowave@localhost:5432/gowave_test?sslmode=disable' go test -count=1 ./...
```
