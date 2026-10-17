---
title: С Remnawave
description: Перенос данных из PostgreSQL Remnawave в GoWave.
sidebar:
  order: 1
---

[Установщик](../../install/installer/) сам находит Remnawave и PasarGuard и предлагает перенос. Команды ниже - для ручного запуска. Исходные базы во всех сценариях только читаются.

Перенос из PostgreSQL Remnawave в файл SQLite:

```bash
gowave migrate pg-to-sqlite
```

- Настройки подключения находятся сами в `/opt/remnawave/.env`.
- Переносятся все таблицы: пользователи, трафик, ноды, хосты, шаблоны, сквады.
- Исходная база и `.env` не меняются. По умолчанию создаётся `gowave-migrated.sqlite`: укажите его в `DATABASE_URL` с `DB_DRIVER=sqlite` и перезапустите GoWave. Установщик делает это сам.
- Интерактивное меню (`gowave rescue`) после переноса предложит остановить и удалить контейнеры `remnawave`, `remnawave-db`, `remnawave-redis` - только после подтверждения.
