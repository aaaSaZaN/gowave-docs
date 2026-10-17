---
title: PostgreSQL 17 → 18
description: Upgrading the database of a Docker GoWave install from PostgreSQL 17 to 18.
sidebar:
  order: 5
---

New Docker installs come with PostgreSQL 18. Earlier installs stay on PostgreSQL 17: `docker compose pull` does not touch the compose file, so the database version stays the same. PostgreSQL 17 is supported until November 2029, so upgrading is optional.

## What changed in the image

The `postgres:18` image keeps data in `/var/lib/postgresql/18/docker`, so the volume is mounted at `/var/lib/postgresql` instead of `/var/lib/postgresql/data`. Changing only the image tag does not work, because each major version has its own file format. A version 18 container refuses to start and reports old-version data in `/var/lib/postgresql`. The data itself is left alone.

There are two ways to move the database:

- **pgautoupgrade** is faster: it runs `pg_upgrade` right inside the volume;
- **dump and restore** uses only official tools but loads the database again from scratch.

The commands below assume `/opt/gowave-docker` and the `gowave_postgres_data` volume. If the project lives elsewhere, change the path. `docker volume ls | grep postgres_data` shows the volume name.

## Backup

Required for either method:

```bash
cd /opt/gowave-docker
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > gowave-pg17.sql
ls -lh gowave-pg17.sql
```

The file must not be empty. Keep a copy off the server as well.

## Method 1. pgautoupgrade

:::caution[Community image]
[pgautoupgrade](https://github.com/pgautoupgrade/docker-pgautoupgrade) is not an official PostgreSQL or Docker image; the community maintains it. It upgrades the data in place: if the process is interrupted, the volume cannot be repaired and the database has to be restored from the backup.
:::

```bash
cd /opt/gowave-docker

# User, database and password from the running container
docker compose exec -T postgres env | grep '^POSTGRES_' > pg-upgrade.env
docker compose down

docker run --rm --env-file pg-upgrade.env -e PGAUTO_ONESHOT=yes \
  -v gowave_postgres_data:/var/lib/postgresql \
  pgautoupgrade/pgautoupgrade:18-alpine
rm pg-upgrade.env
```

It should finish with `Upgrade to PostgreSQL 18.x complete.` and a message that one-shot mode is exiting. Then change the image and the volume path in the compose file and start the project:

```bash
sed -i 's#image: postgres:17-alpine#image: postgres:18-alpine#; s#- postgres_data:/var/lib/postgresql/data#- postgres_data:/var/lib/postgresql#' docker-compose.yml
docker compose up -d
```

Do not skip `pg-upgrade.env`. pgautoupgrade connects as the user from `POSTGRES_USER` to the database from `POSTGRES_DB`. Without them it looks for a `postgres` user and stops halfway, leaving the volume in a state that a second run cannot fix.

:::note[Why alpine]
GoWave uses the alpine PostgreSQL image, so pgautoupgrade is used in its `-alpine` variant as well. Guides for Remnawave use `18-trixie` because that database was created on Debian. Moving from alpine to Debian also switches the C library from musl to glibc, which changes how strings sort in indexes.
:::

## Method 2. Dump and restore

```bash
cd /opt/gowave-docker
docker compose down
docker volume rm gowave_postgres_data   # deletes the 17 database; the backup is in gowave-pg17.sql

sed -i 's#image: postgres:17-alpine#image: postgres:18-alpine#; s#- postgres_data:/var/lib/postgresql/data#- postgres_data:/var/lib/postgresql#' docker-compose.yml

# PostgreSQL first: the panel must not create an empty schema before the restore
docker compose up -d postgres
docker compose exec -T postgres sh -c 'until pg_isready -q -h 127.0.0.1; do sleep 1; done; PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < gowave-pg17.sql > /dev/null
docker compose up -d
```

The wait for `pg_isready -h 127.0.0.1` matters because of how a new container starts. While the database is being created, the image runs a temporary server reachable only through a socket and then restarts it. A restore started at that moment gets cut off.

The same method works as a rollback if pgautoupgrade fails.

## Checking the result

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "select version()"'
docker compose ps
```

The version should start with `PostgreSQL 18` and both containers should be `healthy`. Log in to the panel and check users and nodes. Once everything works, you can delete `gowave-pg17.sql`.
