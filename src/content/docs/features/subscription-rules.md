---
title: Правила ответов (SRR)
description: Как панель решает, что отдать клиенту по ссылке подписки. Условия, типы ответа, модификации и примеры.
sidebar:
  order: 9
---

Одна и та же ссылка подписки отдаёт разное в зависимости от того, кто её открыл: Happ получит Xray JSON, Clash Verge получит YAML для Mihomo, браузер увидит страницу с информацией. Решают это правила ответов, Response Rules (SRR). Они хранятся в настройках подписки, в панели они редактируются на странице «Правила ответов» в разделе «Подписка».

## Как выбирается ответ

1. Если у запроса нет заголовка `User-Agent`, панель отвечает `403`.
2. Если тип клиента указан в пути (`/api/sub/<shortUuid>/singbox`), правила не проверяются, см. [ниже](#тип-клиента-в-пути).
3. Иначе правила проверяются по порядку сверху вниз. Срабатывает первое включённое правило, у которого выполнились условия. Остальные уже не смотрятся.
4. Если ни одно правило не подошло, ответ `403`.

Правило без условий срабатывает всегда, поэтому его ставят последним как запасной вариант. В стандартных правилах это «Fallback Base64».

## Структура

```json
{
  "version": "1",
  "settings": { "disableSubscriptionAccessByPath": false },
  "rules": [
    {
      "name": "Happ",
      "description": "Happ получает Xray JSON",
      "enabled": true,
      "operator": "AND",
      "conditions": [
        { "headerName": "user-agent", "operator": "STARTS_WITH", "value": "Happ/", "caseSensitive": true }
      ],
      "responseType": "XRAY_JSON",
      "responseModifications": { "disableHwidCheck": false }
    }
  ]
}
```

| Поле правила | Обязательно | Описание |
| :--- | :--- | :--- |
| `name` | да | От 1 до 50 символов. Попадает в историю запросов подписки |
| `description` | нет | До 250 символов |
| `enabled` | да | Выключенные правила пропускаются |
| `operator` | да | `AND`: должны выполниться все условия. `OR`: достаточно одного |
| `conditions` | да | Список условий, может быть пустым |
| `responseType` | да | Что отдать, см. [типы ответа](#типы-ответа) |
| `responseModifications` | нет | Дополнительные изменения ответа, см. [модификации](#модификации) |

## Условия

Каждое условие проверяет один заголовок запроса.

| Поле | Описание |
| :--- | :--- |
| `headerName` | Имя заголовка, регистр не важен: `user-agent`, `accept`, `x-forwarded-for` и любые другие |
| `operator` | Как сравнивать, список ниже |
| `value` | Строка для сравнения, от 1 до 255 символов |
| `caseSensitive` | `false`, чтобы сравнивать без учёта регистра |

Операторы: `EQUALS`, `NOT_EQUALS`, `CONTAINS`, `NOT_CONTAINS`, `STARTS_WITH`, `NOT_STARTS_WITH`, `ENDS_WITH`, `NOT_ENDS_WITH`, `REGEX`, `NOT_REGEX`.

:::caution[Нет заголовка, значит условие не выполнено]
Если заголовка в запросе нет, условие считается невыполненным для **любого** оператора, в том числе для `NOT_EQUALS` и `NOT_CONTAINS`.
:::

Регулярные выражения работают в синтаксисе RE2, как в Go. Lookahead, lookbehind и обратные ссылки не поддерживаются. Выражение с ошибкой не совпадает ни с чем.

Чтобы привязать правило к пользователю, используйте служебный заголовок. Перед проверкой панель добавляет к заголовкам служебный `x-remnawave-injected-short-uuid` с коротким UUID из ссылки, и правило с условием на него сработает только для этих пользователей.

## Типы ответа

| `responseType` | Ответ |
| :--- | :--- |
| `XRAY_JSON` | Конфиг Xray JSON, см. [шаблоны Xray JSON](../templates/) |
| `XRAY_BASE64` | Список ссылок `vless://`, `trojan://` и других в base64 |
| `MIHOMO` | YAML для Mihomo (Clash Meta) |
| `STASH` | YAML для Stash |
| `CLASH` | YAML для классического Clash |
| `SINGBOX` | JSON для sing-box |
| `BROWSER` | JSON с информацией о подписке, его показывает страница подписки |
| `BLOCK` | `403 Forbidden` |
| `STATUS_CODE_404` | `404 Not Found` |
| `STATUS_CODE_451` | `451 Unavailable For Legal Reasons` |
| `SOCKET_DROP` | Соединение рвётся без ответа (TCP RST) |

`SOCKET_DROP` полезен против сканеров: со стороны соединение выглядит так, будто сервера нет.

## Модификации

Объект `responseModifications` меняет ответ сработавшего правила.

| Поле | Что делает |
| :--- | :--- |
| `headers` | Список заголовков `{ "key", "value" }`, которые добавятся к ответу |
| `applyHeadersToEnd` | `false`: заголовки ставятся до формирования ответа, и стандартные заголовки подписки (`subscription-userinfo`, `content-disposition` и заданные в настройках) могут их перезаписать. `true`: заголовки ставятся последними и перезаписывают стандартные |
| `subscriptionTemplate` | Имя шаблона подписки нужного типа вместо шаблона по умолчанию |
| `ignoreHostXrayJsonTemplate` | Не использовать шаблоны Xray JSON, заданные у отдельных хостов, только общий |
| `ignoreServeJsonAtBaseSubscription` | Не подменять base64 на JSON для этого правила, см. [ниже](#json-вместо-base64) |
| `disableHwidCheck` | Не проверять лимит устройств HWID. Устройство всё равно запишется |
| `additionalExtendedClientsRegex` | Регулярные выражения для `User-Agent`, которые сделают клиента «расширенным», см. [ниже](#расширенные-клиенты) |
| `encryption` | Зашифровать ответ, см. [ниже](#шифрование) |
| `excludeHostsByTags` | Убрать из ответа хосты с этими тегами. Теги в формате `A-Z`, `0-9`, `_`, `:`, до 36 символов |
| `respondWithRemarks` | Вместо серверов отдать записи с этими подписями, например сообщение «обновите приложение» |

:::note[respondWithRemarks]
Работает только при включённой настройке подписки «Показывать свои примечания» (`isShowCustomRemarks`). Без неё клиент получит пустую подписку. В подписях можно использовать [переменные](../template-variables/).
:::

Если у пользователя есть внешний сквад со своим шаблоном и в правиле не задан `subscriptionTemplate`, панель возьмёт шаблон сквада.

## Тип клиента в пути

Ссылку можно открыть с явным типом: `/api/sub/<shortUuid>/<тип>`. Тогда правила не проверяются.

| Путь | Ответ |
| :--- | :--- |
| `json`, `v2ray-json` | `XRAY_JSON` |
| `mihomo` | `MIHOMO` |
| `stash` | `STASH` |
| `clash` | `CLASH` |
| `singbox` | `SINGBOX` |
| любой другой | `BLOCK` |

Настройка `settings.disableSubscriptionAccessByPath: true` запрещает такие ссылки: на любой тип в пути панель ответит `403`.

## Расширенные клиенты

Если клиент «расширенный», в его ответ попадает описание сервера, заданное у хоста (`serverDescription`): в Xray JSON как `meta.serverDescription`, в ссылках и в Mihomo как дополнительное поле. Расширенными считаются клиенты, у которых `User-Agent` начинается с `FlClash X/`, `FlClashX/`, `Flowvy/`, `prizrak-box/`, `koala-clash/`, `Happ/` или `INCY/`. Свои варианты добавляются через `additionalExtendedClientsRegex`.

## JSON вместо base64

При включённой настройке подписки «Отдавать JSON на базовом пути подписки» (`serveJsonAtBaseSubscription`) правило с ответом `XRAY_BASE64` отдаёт Xray JSON клиентам, которые его понимают. Их список: `Streisand`, `Happ/`, `INCY/`, `ktor-client`, `V2Box`, `io.github.saeeddev94.xray/`, `v2rayNG/`, `v2rayN/`, `v2plus/`. Модификация `ignoreServeJsonAtBaseSubscription` отключает это для конкретного правила.

## Шифрование

```json
"encryption": { "method": "age1", "key": "age1...публичный_ключ_получателя" }
```

Ответ шифруется в формате [age](https://age-encryption.org) и отдаётся как ASCII-armored текст (`-----BEGIN AGE ENCRYPTED FILE-----`). В `key` указывается публичный ключ получателя: `age1…` для `method: "age1"` или постквантовый `age1pq1…` для `method: "age1pq1"`. Расшифровать ответ может только клиент с парным секретным ключом. Если ключ неверный, ответ будет пустым.

## Примеры

### Блокировать приложение

```json
{
  "name": "Block old v2rayNG",
  "enabled": true,
  "operator": "AND",
  "conditions": [
    { "headerName": "user-agent", "operator": "REGEX", "value": "^v2rayNG/1\\.", "caseSensitive": false }
  ],
  "responseType": "SOCKET_DROP"
}
```

### Сообщение вместо серверов

Нужна настройка «Показывать свои примечания».

```json
{
  "name": "Ask to update",
  "enabled": true,
  "operator": "AND",
  "conditions": [
    { "headerName": "user-agent", "operator": "STARTS_WITH", "value": "Streisand", "caseSensitive": true }
  ],
  "responseType": "XRAY_BASE64",
  "responseModifications": {
    "respondWithRemarks": ["Обновите приложение до Happ", "Осталось дней: {{DAYS_LEFT}}"]
  }
}
```

### Свой шаблон для одного пользователя

```json
{
  "name": "Tester",
  "enabled": true,
  "operator": "AND",
  "conditions": [
    { "headerName": "x-remnawave-injected-short-uuid", "operator": "EQUALS", "value": "Ab3dEf6hIj9kLm2n", "caseSensitive": true }
  ],
  "responseType": "XRAY_JSON",
  "responseModifications": {
    "subscriptionTemplate": "Beta",
    "excludeHostsByTags": ["LEGACY"]
  }
}
```

Правило для конкретного пользователя ставьте выше общих, иначе раньше сработает правило по `User-Agent`.

## Стандартные правила

| Правило | Условие | Ответ |
| :--- | :--- | :--- |
| Browser Subscription | `accept` содержит `text/html` | `BROWSER` |
| Mihomo Clients | `user-agent` ~ `^(?:flclash\|rabbit\|flowvy\|murge\|mihomo\|prizrak-box\|koala-clash\|clash(?:-verge\|-nyanpasu\|x meta\|[-.]?meta))` | `MIHOMO` |
| Stash (iOS, macOS) | `user-agent` ~ `^stash` | `STASH` |
| Sing-box clients | `user-agent` ~ `^sfa\|sfi\|sfm\|sft\|karing\|singbox` | `SINGBOX` |
| Clash Core Clients | `user-agent` ~ `^clash` | `CLASH` |
| Fallback Base64 | без условий | `XRAY_BASE64` |

Регулярные выражения в таблице сравниваются без учёта регистра. «Browser Subscription» и «Fallback Base64» не удаляйте и не выключайте: без первого перестанет работать страница подписки, без второго клиенты с незнакомым `User-Agent` получат `403`.

## Проверка правил

В редакторе правил есть «Отладчик правил ответов». Он показывает, какое правило сработает для заголовков вашего браузера, и выдаёт команду cURL с текущими правилами. В этой команде можно поменять заголовки и проверить любой клиент, не трогая настоящую подписку. Сработавшее правило каждого реального запроса видно в «Инспекторе SRH» в разделе «Инструменты».
