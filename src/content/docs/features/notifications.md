---
title: Уведомления
description: Вебхуки и Telegram - формат запросов, подпись, повторы и настройка отдельных событий.
sidebar:
  order: 4
---

Панель сообщает о событиях двумя способами: в чаты Telegram и вебхуками на ваш адрес. Оба канала включаются переменными окружения, их список - в [справочнике](../../reference/environment/#уведомления). Формат совпадает с Remnawave, поэтому боты и обработчики, написанные под неё, работают без изменений.

## Вебхуки

На каждое событие панель отправляет `POST` с JSON на все адреса из `WEBHOOK_URL`:

```json
{
  "scope": "user",
  "event": "user.expired",
  "timestamp": "2026-11-05T12:00:00.000Z",
  "data": { "uuid": "...", "username": "alice", "status": "EXPIRED" }
}
```

`data` - объект в том же виде, в каком его отдаёт API (пользователь, нода и так далее). У части событий есть ещё поле `meta` с подробностями.

Заголовки запроса:

| Заголовок | Значение |
| :--- | :--- |
| `X-Remnawave-Signature` | HMAC-SHA256 тела запроса, ключ - `WEBHOOK_SECRET_HEADER`, в hex |
| `X-Remnawave-Timestamp` | Время события, то же, что `timestamp` в теле |
| `Content-Type` | `application/json` |
| `User-Agent` | `Remnawave` |

Проверяйте подпись по сырому телу запроса, до разбора JSON. Пример на Python:

```python
import hashlib
import hmac

def is_valid(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Доставка и повторы

События сначала попадают в очередь в базе панели, поэтому переживают перезапуск. На один адрес вебхуки уходят строго по очереди, в порядке событий. Ответ с кодом 2xx считается доставкой. Любой другой код или сетевая ошибка - повтор через 2, 4, 8 секунд и дальше вдвое дольше, но не реже раза в 5 минут. После 10 неудачных попыток событие отбрасывается, а в журнал панели пишется ошибка.

## Telegram

Сообщения уходят в чаты по типу события:

| События | Чат |
| :--- | :--- |
| `user.*` | `TELEGRAM_NOTIFY_USERS` |
| `node.*` | `TELEGRAM_NOTIFY_NODES` |
| `service.*`, `errors.*` | `TELEGRAM_NOTIFY_SERVICE` |
| `crm.*` | `TELEGRAM_NOTIFY_CRM` |
| `torrent_blocker.*` | `TELEGRAM_NOTIFY_TBLOCKER` |

События `user_hwid_devices.*` идут только вебхуками. Для типа без чата Telegram-сообщений не будет. Повторы такие же, как у вебхуков. Если Telegram ответил «слишком много запросов», панель ждёт столько, сколько он попросил.

## Тонкая настройка событий

По умолчанию каждое событие уходит во все включённые каналы. Чтобы выключить лишнее или отправить событие на дополнительный адрес, создайте `notifications-config.yml`:

```yaml
events:
  user.modified:
    telegram: false
    webhook: true
  node.connection_lost:
    telegram: true
    webhook: true
    additionalWebhookUrls:
      - https://alerts.example.com/hook
  service.login_attempt_success:
    telegram: false
    webhook: false
```

- Событие, которого нет в файле, включено во всех каналах.
- У события из файла каждый канал включается только явным `true`.
- `additionalWebhookUrls` добавляются к адресам из `WEBHOOK_URL`. Работают они, только если включён `WEBHOOK_ENABLED`.
- Неизвестное имя события - ошибка: панель не запустится и назовёт его.

Панель ищет файл по порядку и берёт первый найденный:

1. путь из `NOTIFICATIONS_CONFIG_PATH`;
2. `/var/lib/remnawave/configs/notifications/notifications-config.yml` - путь, где его держит Remnawave;
3. `configs/notifications/notifications-config.yml` относительно рабочей папки, на systemd это `/opt/gowave/configs/notifications/`.

Файл читается при запуске, после правки перезапустите панель. В Docker смонтируйте его в контейнер только для чтения, например добавьте в `volumes` сервиса `gowave`:

```yaml
    volumes:
      - ./notifications-config.yml:/var/lib/remnawave/configs/notifications/notifications-config.yml:ro
```

### Все события

| Тип | События |
| :--- | :--- |
| `user` | `user.created`, `user.modified`, `user.deleted`, `user.revoked`, `user.disabled`, `user.enabled`, `user.limited`, `user.expired`, `user.traffic_reset`, `user.first_connected`, `user.bandwidth_usage_threshold_reached`, `user.not_connected`, `user.expiration` |
| `user_hwid_devices` | `user_hwid_devices.added`, `user_hwid_devices.deleted` |
| `node` | `node.created`, `node.modified`, `node.disabled`, `node.enabled`, `node.deleted`, `node.connection_lost`, `node.connection_restored`, `node.traffic_notify` |
| `service` | `service.panel_started`, `service.login_attempt_failed`, `service.login_attempt_success`, `service.subpage_config_changed`, `service.api_token_created`, `service.api_token_deleted` |
| `errors` | `errors.bandwidth_usage_threshold_reached_max_notifications` |
| `crm` | `crm.infra_billing_node_payment_in_7_days`, `crm.infra_billing_node_payment_in_48hrs`, `crm.infra_billing_node_payment_in_24hrs`, `crm.infra_billing_node_payment_due_today`, `crm.infra_billing_node_payment_overdue_24hrs`, `crm.infra_billing_node_payment_overdue_48hrs`, `crm.infra_billing_node_payment_overdue_7_days` |
| `torrent_blocker` | `torrent_blocker.report` |

`user.bandwidth_usage_threshold_reached`, `user.not_connected` и `user.expiration` срабатывают только при включённых [пороговых уведомлениях](../../reference/environment/#пороговые-уведомления).
