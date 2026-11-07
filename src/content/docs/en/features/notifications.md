---
title: Notifications
description: Webhooks and Telegram - request format, signature, retries and per-event settings.
sidebar:
  order: 4
---

The panel reports events in two ways: to Telegram chats and as webhooks to your own endpoint. Both are turned on with environment variables, listed in the [reference](../../reference/environment/#notifications). The format matches Remnawave, so bots and handlers written for it work unchanged.

## Webhooks

For every event the panel sends a `POST` with JSON to each address in `WEBHOOK_URL`:

```json
{
  "scope": "user",
  "event": "user.expired",
  "timestamp": "2026-11-05T12:00:00.000Z",
  "data": { "uuid": "...", "username": "alice", "status": "EXPIRED" }
}
```

`data` is the object as the API returns it (a user, a node and so on). Some events also carry a `meta` field with details.

Request headers:

| Header | Value |
| :--- | :--- |
| `X-Remnawave-Signature` | HMAC-SHA256 of the request body keyed with `WEBHOOK_SECRET_HEADER`, in hex |
| `X-Remnawave-Timestamp` | Event time, the same as `timestamp` in the body |
| `Content-Type` | `application/json` |
| `User-Agent` | `Remnawave` |

Check the signature against the raw request body, before parsing the JSON. A Python example:

```python
import hashlib
import hmac

def is_valid(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Delivery and retries

Events go to a queue in the panel database first, so they survive a restart. Webhooks to one address are sent one at a time, in event order. A 2xx answer counts as delivered. Any other status or a network error is retried after 2, 4, 8 seconds and so on, doubling each time but never waiting more than 5 minutes. After 10 failed attempts the event is dropped and the panel logs an error.

## Telegram

Messages go to chats by event type:

| Events | Chat |
| :--- | :--- |
| `user.*` | `TELEGRAM_NOTIFY_USERS` |
| `node.*` | `TELEGRAM_NOTIFY_NODES` |
| `service.*`, `errors.*` | `TELEGRAM_NOTIFY_SERVICE` |
| `crm.*` | `TELEGRAM_NOTIFY_CRM` |
| `torrent_blocker.*` | `TELEGRAM_NOTIFY_TBLOCKER` |

`user_hwid_devices.*` events are sent only as webhooks, never to Telegram. If a type has no chat, its messages go nowhere. Retries work as for webhooks; when Telegram answers "too many requests", the panel waits as long as Telegram asks.

## Per-event settings

By default every event goes to every enabled channel. To turn some off or send an event to an extra address, create `notifications-config.yml`:

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

- An event missing from the file is on in every channel.
- For an event listed in the file, each channel is on only with an explicit `true`.
- `additionalWebhookUrls` are added to the `WEBHOOK_URL` addresses. They work only when `WEBHOOK_ENABLED` is on.
- An unknown event name is an error: the panel refuses to start and names it.

The panel looks for the file in this order and takes the first one it finds:

1. the path in `NOTIFICATIONS_CONFIG_PATH`;
2. `/var/lib/remnawave/configs/notifications/notifications-config.yml`, where Remnawave keeps it;
3. `configs/notifications/notifications-config.yml` relative to the working directory, which is `/opt/gowave/configs/notifications/` on systemd.

The file is read at startup, so restart the panel after editing it. In Docker, mount it read-only, for example by adding to the `volumes` of the `gowave` service:

```yaml
    volumes:
      - ./notifications-config.yml:/var/lib/remnawave/configs/notifications/notifications-config.yml:ro
```

### All events

| Type | Events |
| :--- | :--- |
| `user` | `user.created`, `user.modified`, `user.deleted`, `user.revoked`, `user.disabled`, `user.enabled`, `user.limited`, `user.expired`, `user.traffic_reset`, `user.first_connected`, `user.bandwidth_usage_threshold_reached`, `user.not_connected`, `user.expiration` |
| `user_hwid_devices` | `user_hwid_devices.added`, `user_hwid_devices.deleted` |
| `node` | `node.created`, `node.modified`, `node.disabled`, `node.enabled`, `node.deleted`, `node.connection_lost`, `node.connection_restored`, `node.traffic_notify` |
| `service` | `service.panel_started`, `service.login_attempt_failed`, `service.login_attempt_success`, `service.subpage_config_changed`, `service.api_token_created`, `service.api_token_deleted` |
| `errors` | `errors.bandwidth_usage_threshold_reached_max_notifications` |
| `crm` | `crm.infra_billing_node_payment_in_7_days`, `crm.infra_billing_node_payment_in_48hrs`, `crm.infra_billing_node_payment_in_24hrs`, `crm.infra_billing_node_payment_due_today`, `crm.infra_billing_node_payment_overdue_24hrs`, `crm.infra_billing_node_payment_overdue_48hrs`, `crm.infra_billing_node_payment_overdue_7_days` |
| `torrent_blocker` | `torrent_blocker.report` |

`user.bandwidth_usage_threshold_reached`, `user.not_connected` and `user.expiration` fire only with [threshold notifications](../../reference/environment/#threshold-notifications) turned on.
