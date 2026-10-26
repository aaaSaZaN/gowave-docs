---
title: PostgreSQL 17 → 18
description: Обновление базы в Docker-установке GoWave с PostgreSQL 17 до 18.
sidebar:
  order: 5
---

Новые установки в Docker ставятся со стандартным образом `postgres:18`. Установки, сделанные раньше, остаются на PostgreSQL 17: `docker compose pull` не меняет compose-файл, а вместе с ним и версию базы. PostgreSQL 17 поддерживается до ноября 2029 года, так что обновляться не обязательно.

## Что изменилось в образе

Образ `postgres:18` хранит данные в `/var/lib/postgresql/18/docker`, поэтому том монтируется в `/var/lib/postgresql`, а не в `/var/lib/postgresql/data`. Сменить только тег образа нельзя: формат файлов у каждой основной версии свой. Контейнер с 18 не запустится и сообщит, что в `/var/lib/postgresql` лежат данные старой версии. Сами данные при этом не трогаются.

Перенести базу можно двумя способами:

- **pgautoupgrade** - быстрее, `pg_upgrade` прямо в томе;
- **дамп и восстановление** - только официальные инструменты, но база загружается заново.

Команды ниже рассчитаны на `/opt/gowave-docker` и том `gowave_postgres_data`. Если проект лежит в другой папке, замените путь. Имя тома покажет `docker volume ls | grep postgres_data`.

## Резервная копия

Обязательна при любом способе:

```bash
cd /opt/gowave-docker
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > gowave-pg17.sql
ls -lh gowave-pg17.sql
```

Файл должен быть не пустым. Скопируйте его ещё и за пределы сервера.

## Способ 1. pgautoupgrade

:::caution[Образ сообщества]
[pgautoupgrade](https://github.com/pgautoupgrade/docker-pgautoupgrade) - не официальный образ PostgreSQL или Docker, его поддерживает сообщество. Он обновляет данные на месте: если процесс прервётся, исправить том уже не получится, и база восстанавливается из копии.
:::

```bash
cd /opt/gowave-docker

# Пользователь, база и пароль из работающего контейнера
docker compose exec -T postgres env | grep '^POSTGRES_' > pg-upgrade.env
docker compose down

docker run --rm --env-file pg-upgrade.env -e PGAUTO_ONESHOT=yes \
  -v gowave_postgres_data:/var/lib/postgresql \
  pgautoupgrade/pgautoupgrade:18-debian
rm pg-upgrade.env
```

В конце должна появиться строка `Upgrade to PostgreSQL 18.x complete.` и сообщение о выходе в режиме one shot. Затем поменяйте образ и путь тома в compose и запустите проект:

```bash
sed -i 's#image: postgres:17.*#image: postgres:18#; s#- postgres_data:/var/lib/postgresql/data#- postgres_data:/var/lib/postgresql#' docker-compose.yml
docker compose up -d
```

Без `pg-upgrade.env` ничего не выйдет: pgautoupgrade подключается под пользователем из `POSTGRES_USER` к базе из `POSTGRES_DB`. Если их не передать, он ищет пользователя `postgres` и останавливается посередине, оставив том в состоянии, которое повторный запуск уже не исправит.

## Способ 2. Дамп и восстановление

```bash
cd /opt/gowave-docker
docker compose down
docker volume rm gowave_postgres_data   # удаляет базу 17, копия уже в gowave-pg17.sql

sed -i 's#image: postgres:17.*#image: postgres:18#; s#- postgres_data:/var/lib/postgresql/data#- postgres_data:/var/lib/postgresql#' docker-compose.yml

# Сначала только PostgreSQL: панель не должна создать пустую схему раньше восстановления
docker compose up -d postgres
docker compose exec -T postgres sh -c 'until pg_isready -q -h 127.0.0.1; do sleep 1; done; PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < gowave-pg17.sql > /dev/null
docker compose up -d
```

Ожидание `pg_isready -h 127.0.0.1` нужно из-за того, как стартует новый контейнер. Пока база создаётся, образ запускает временный сервер, доступный только через сокет, а потом перезапускает его. Восстановление, начатое в этот момент, оборвётся.

Этот же способ годится как откат, если pgautoupgrade не справился.

## Проверка

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "select version()"'
docker compose ps
```

Версия должна начинаться с `PostgreSQL 18`, оба контейнера - в состоянии `healthy`. Войдите в панель и проверьте пользователей и ноды. Когда всё работает, файл `gowave-pg17.sql` можно удалить.
