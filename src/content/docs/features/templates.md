---
title: Шаблоны Xray JSON
description: Как собирается подписка Xray JSON, подстановка хостов через блок remnawave, шаблоны Mihomo и sing-box, маппер хоста.
sidebar:
  order: 10
---

Шаблоны подписки лежат в разделе «Подписка» на странице шаблонов. Для каждого формата (Xray JSON, Mihomo, Stash, Clash, sing-box) можно держать несколько шаблонов: один основной, остальные выбирают [правила ответа](../subscription-rules/) через `subscriptionTemplate` или внешние сквады.

## Как собирается Xray JSON

Шаблон Xray JSON устроен как обычный конфиг Xray: `log`, `dns`, `inbounds`, `routing`, `outbounds` и всё остальное. Подписка состоит из таких конфигов, по одному на каждый хост пользователя:

1. Берётся шаблон: шаблон хоста, если он задан у хоста, иначе общий. Правило с `ignoreHostXrayJsonTemplate` всегда берёт общий.
2. Из хоста собирается outbound с тегом `proxy` и ставится **первым** в `outbounds`, перед outbound'ами шаблона.
3. В `remarks` записывается подпись хоста. Для [расширенных клиентов](../subscription-rules/#расширенные-клиенты) добавляется `meta.serverDescription`.

Скрытые хосты и хосты, у которых Xray JSON исключён из типов подписки, пропускаются.

Поэтому маршрутизация в шаблоне ссылается на тег `proxy`:

```json
{
  "routing": {
    "rules": [
      { "type": "field", "domain": ["geosite:private"], "outboundTag": "direct" },
      { "type": "field", "network": "tcp,udp", "outboundTag": "proxy" }
    ]
  },
  "outbounds": [
    { "tag": "direct", "protocol": "freedom" },
    { "tag": "block", "protocol": "blackhole" }
  ]
}
```

## Блок `remnawave`: несколько хостов в одном конфиге

Если в шаблоне есть объект `remnawave`, панель собирает конфиг иначе: в `outbounds` попадают те хосты, которые вы выберете. Так делаются балансировщики, резервные серверы и цепочки. Сам блок `remnawave` в ответ не попадает.

```json
{
  "remnawave": {
    "addVirtualHostAsOutbound": true,
    "injectHosts": [
      {
        "selector": { "type": "remarkRegex", "pattern": "^Резерв" },
        "selectFrom": "HIDDEN",
        "tagPrefix": "backup"
      }
    ]
  },
  "routing": {
    "balancers": [{ "tag": "auto", "selector": ["proxy", "backup"], "strategy": { "type": "leastPing" } }],
    "rules": [{ "type": "field", "network": "tcp,udp", "balancerTag": "auto" }]
  },
  "observatory": { "subjectSelector": ["proxy", "backup"], "probeUrl": "https://www.gstatic.com/generate_204" },
  "outbounds": [{ "tag": "direct", "protocol": "freedom" }]
}
```

Конфиг всё так же собирается для каждого хоста, и хост, для которого он собирается, дальше называется «текущим».

| Поле | Описание |
| :--- | :--- |
| `addVirtualHostAsOutbound` | `true`: текущий хост добавляется с тегом `proxy` |
| `injectHosts` | Список выборок, каждая добавляет найденные хосты как outbound'ы |

Найденные outbound'ы ставятся перед outbound'ами шаблона, в порядке выборок.

:::caution[Пустой блок убирает хост]
Если блок `remnawave` есть, но `addVirtualHostAsOutbound` не включён и `injectHosts` пуст, конфиг для хоста не собирается и хост пропадает из подписки.
:::

### Выборка хостов

| Поле | Описание |
| :--- | :--- |
| `selector` | Какие хосты выбрать, см. таблицу ниже. Обязателен |
| `selectFrom` | Из каких хостов выбирать: `HIDDEN` (по умолчанию, только скрытые), `NOT_HIDDEN` или `ALL`. Текущий хост в выборку не попадает никогда |
| `tagPrefix` | Теги outbound'ов: `<префикс>`, `<префикс>-2`, `<префикс>-3` и так далее. По умолчанию `proxy` |
| `useHostRemarkAsTag` | `true`: тегом станет подпись хоста |
| `useHostTagAsTag` | `true`: тегом станет первый тег хоста, а если тегов нет, то подпись |

Если заданы и `useHostRemarkAsTag`, и `useHostTagAsTag`, побеждает первый. `tagPrefix` действует, когда оба выключены.

| `selector.type` | Параметры | Какие хосты |
| :--- | :--- | :--- |
| `uuids` | `values`: список UUID | Хосты с этими UUID, в порядке списка |
| `remarkRegex` | `pattern` | Подпись совпадает с выражением |
| `tagRegex` | `pattern` | Хотя бы один тег хоста совпадает с выражением |
| `sameTagAsRecipient` | нет | Хосты, у которых есть общий тег с текущим |

Регулярные выражения работают в синтаксисе RE2: без lookahead, lookbehind и обратных ссылок. Выражение с ошибкой не находит ничего.

Скрытые хосты удобны как «запасные части»: пользователь не видит их отдельными серверами, но они подставляются в конфиги видимых хостов. Чтобы теги не пересекались с `proxy` текущего хоста, задавайте для выборок свой `tagPrefix`.

## Шаблоны Mihomo и Stash

Сервера добавляются в конец `proxies` шаблона, а их имена (подписи хостов) дописываются в каждую группу `proxy-groups`. Хосты с транспортом `kcp` пропускаются, для Stash также `xhttp`.

Управлять этим можно блоками `remnawave`:

| Где | Поле | Что делает |
| :--- | :--- | :--- |
| Корень шаблона (Mihomo) | `includeHiddenHosts: true` | Добавлять и скрытые хосты |
| Группа в `proxy-groups` | `include-proxies: false` | Не дописывать сервера в эту группу |
| Группа в `proxy-groups` | `select-random-proxy: true` | Дописать один случайный сервер |
| Группа в `proxy-groups` | `shuffle-proxies-order: true` | Дописать все сервера в случайном порядке |
| Провайдер в `proxy-providers` (Mihomo) | `include-proxies: true` | Положить все сервера в `payload` провайдера |

```yaml
proxy-groups:
  - name: Авто
    type: url-test
    url: https://www.gstatic.com/generate_204
    interval: 300
  - name: Резерв
    type: select
    proxies: [DIRECT]
    remnawave:
      shuffle-proxies-order: true
```

## Шаблон sing-box

Сервера добавляются в `outbounds`, а их теги дописываются во все outbound'ы типа `selector` и `urltest`. Чтобы какой-то из них оставить как есть, добавьте ему `"remnawave": { "includeProxies": false }`.

## Маппер хоста

У каждого хоста есть поле маппера: операции, которые меняют уже собранный для этого хоста кусок подписки. Операции задаются отдельно для каждого формата: `xrayJson`, `mihomo`, `singbox`, `base64`.

```json
{
  "xrayJson": [
    { "op": "set", "to": "streamSettings.sockopt.tcpFastOpen", "value": true },
    { "op": "copy", "from": "$host.metadata.remark", "to": "tag" },
    { "op": "unset", "to": "mux" }
  ]
}
```

| `op` | Поля | Действие |
| :--- | :--- | :--- |
| `set` | `to`, `value` | Записать значение по пути |
| `copy` | `from`, `to` | Скопировать значение из инбаунда или из хоста |
| `unset` | `to` | Удалить значение |

- `to` задаёт путь внутри собранного объекта через точку: outbound Xray, прокси Mihomo, outbound sing-box.
- `from` без префикса указывает путь внутри исходного инбаунда из профиля конфигурации, а с префиксом `$host.` берёт поле хоста. Доступны `address`, `port`, `protocol`, `finalRemark`, `mux`, `security`, `securityOptions`, `transport`, `transportOptions`, `protocolOptions`, `metadata.inboundTag`, `metadata.remark`, `metadata.tags`, `clientOverrides.serverDescription`, `streamOverrides.finalMask`, `streamOverrides.sockopt` и вложенные в них поля.
- Операция пропускается, если источника нет или путь проходит через простое значение (строку или число).
- В `base64` можно менять параметры ссылки (в `to` пишется имя параметра) и саму ссылку через `$link.address`, `$link.port`, `$link.password`, `$link.method`, `$link.remark`.
