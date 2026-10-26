---
title: С Docker-ноды на Go-ноду
description: Перевод ноды с образа remnawave/node на Go-ноду.
sidebar:
  order: 4
---

Если нода работает в Docker на образе `remnawave/node`, её переводит на Go-ноду тот же установщик (от root на сервере ноды):

```bash
sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/remnanode-go/main/install.sh)"
```

Установщик находит контейнер и переносит его окружение (`SECRET_KEY`, `NODE_PORT` и остальное) в `.env` Go-ноды, поэтому в панели ничего менять не нужно.
