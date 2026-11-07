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

Без этих флагов бинарник показывает версию, записанную в исходниках, и канал stable. Релизы задают версию, канал и коммит через `-ldflags`:

```bash
go build -trimpath -ldflags="-s -w \
  -X gowave/internal/system.AppVersion=v1.2.3 \
  -X gowave/internal/system.Channel=stable \
  -X gowave/internal/system.CommitSha=$(git rev-parse HEAD)" \
  -o gowave-linux-amd64 ./cmd/server
```

## Docker-образ

Собрать образ из исходников вместо `ghcr.io`:

```bash
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

Образ собирается в три стадии: веб-интерфейс на `oven/bun` (один раз, он не зависит от архитектуры), бэкенд на `golang` с кросс-компиляцией без QEMU и итоговый образ на `alpine`. Версию передают аргументы сборки `VERSION`, `CHANNEL` (`stable` или `dev`) и `COMMIT_SHA`.

## Публикация сборок

- Пуш в `main`: после CI workflow `dev.yml` пересобирает пре-релиз `dev` и образы `:dev` и `:dev-<sha>`. Пуши, которые меняют только Markdown, сборку не запускают.
- Тег `v1.2.3`: workflow `release.yml` прогоняет CI и публикует stable-релиз и образы `:1.2.3` и `:latest`. Тег с дефисом (`v1.2.3-beta.1`) становится пре-релизом и `latest` не двигает.

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
