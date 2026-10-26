---
title: CLI и обновление
description: Команды remnanode, обновление ноды и ядра Xray.
sidebar:
  order: 3
---

## Команды

| Команда | Что делает |
| :--- | :--- |
| `remnanode status` | Состояние ноды и ядра |
| `remnanode status --wait-ready` | Дождаться, пока нода получит конфигурацию и Xray запустится |
| `remnanode logs -n 100 -f` | Журнал ноды |
| `remnanode xlogs -n 100 -f` | Журнал Xray |
| `remnanode restart` | Перезапуск |
| `remnanode update -y` | Обновить ноду до последнего релиза |
| `remnanode core install -y` | Поставить последнюю стабильную версию Xray |
| `remnanode core install --version v26.7.28 -y` | Поставить конкретную версию Xray |
| `remnanode core reset` | Вернуть стандартное ядро вместо своего |

Запускайте команды от пользователя службы, обычно root: CLI находит ноду через служебный файл в `/run/remnanode`.

## Обновление из панели

В карточке Go-ноды нажмите на версию Xray Core: откроется выбор официального release или pre-release, а также поле для прямой HTTPS-ссылки на бинарник или архив. Версия самой ноды выбирается на вкладке **Remnanode Go**, список берётся из релизов remnanode-go.
