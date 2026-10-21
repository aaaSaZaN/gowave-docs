---
title: Response rules (SRR)
description: How the panel decides what a subscription link returns. Conditions, response types, modifications and examples.
sidebar:
  order: 9
---

The same subscription link returns different things depending on who opens it: Happ gets Xray JSON, Clash Verge gets Mihomo YAML, a browser gets a page with subscription details. Response Rules (SRR) make that decision. They live in the subscription settings and are edited on the **Response rules** page of the Subscription section.

## How a response is chosen

1. A request without a `User-Agent` header gets `403`.
2. If the client type is in the path (`/api/sub/<shortUuid>/singbox`), the rules are skipped, see [below](#client-type-in-the-path).
3. Otherwise the rules are checked from top to bottom. The first enabled rule whose conditions match wins; the rest are not checked.
4. If no rule matches, the answer is `403`.

A rule without conditions always matches, so it goes last as the fallback. In the default rules that is "Fallback Base64".

## Structure

```json
{
  "version": "1",
  "settings": { "disableSubscriptionAccessByPath": false },
  "rules": [
    {
      "name": "Happ",
      "description": "Happ gets Xray JSON",
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

| Rule field | Required | Description |
| :--- | :--- | :--- |
| `name` | yes | 1 to 50 characters. Recorded in the subscription request history |
| `description` | no | Up to 250 characters |
| `enabled` | yes | Disabled rules are skipped |
| `operator` | yes | `AND`: every condition must match. `OR`: one is enough |
| `conditions` | yes | List of conditions, may be empty |
| `responseType` | yes | What to return, see [response types](#response-types) |
| `responseModifications` | no | Extra changes to the response, see [modifications](#modifications) |

## Conditions

Each condition checks one request header.

| Field | Description |
| :--- | :--- |
| `headerName` | Header name, case-insensitive: `user-agent`, `accept`, `x-forwarded-for` or any other |
| `operator` | How to compare, list below |
| `value` | String to compare with, 1 to 255 characters |
| `caseSensitive` | `false` to ignore case |

Operators: `EQUALS`, `NOT_EQUALS`, `CONTAINS`, `NOT_CONTAINS`, `STARTS_WITH`, `NOT_STARTS_WITH`, `ENDS_WITH`, `NOT_ENDS_WITH`, `REGEX`, `NOT_REGEX`.

:::caution[A missing header never matches]
If the header is absent, the condition fails for **every** operator, including `NOT_EQUALS` and `NOT_CONTAINS`.
:::

Regular expressions use RE2 syntax, as in Go. Lookahead, lookbehind and backreferences are not supported, and an invalid expression matches nothing.

To target specific users, use a service header. Before checking, the panel adds `x-remnawave-injected-short-uuid` with the short UUID from the link, so a condition on it limits the rule to those users.

## Response types

| `responseType` | Response |
| :--- | :--- |
| `XRAY_JSON` | Xray JSON config, see [Xray JSON templates](../templates/) |
| `XRAY_BASE64` | Base64 list of `vless://`, `trojan://` and other links |
| `MIHOMO` | YAML for Mihomo (Clash Meta) |
| `STASH` | YAML for Stash |
| `CLASH` | YAML for classic Clash |
| `SINGBOX` | JSON for sing-box |
| `BROWSER` | JSON with subscription details, shown by the subscription page |
| `BLOCK` | `403 Forbidden` |
| `STATUS_CODE_404` | `404 Not Found` |
| `STATUS_CODE_451` | `451 Unavailable For Legal Reasons` |
| `SOCKET_DROP` | The connection is reset without a response (TCP RST) |

`SOCKET_DROP` is useful against scanners: from outside it looks as if nothing is there.

## Modifications

The `responseModifications` object changes the response of the matched rule.

| Field | What it does |
| :--- | :--- |
| `headers` | List of `{ "key", "value" }` headers added to the response, see [example](#add-a-header-for-a-client) |
| `applyHeadersToEnd` | `false`: headers are set before the response is built, so the standard subscription headers (`subscription-userinfo`, `content-disposition` and those from settings) can overwrite them. `true`: headers are set last and overwrite the standard ones |
| `subscriptionTemplate` | Name of a subscription template of the matching type to use instead of the default |
| `ignoreHostXrayJsonTemplate` | Ignore per-host Xray JSON templates and use only the main one |
| `ignoreServeJsonAtBaseSubscription` | Do not swap base64 for JSON for this rule, see [below](#json-instead-of-base64) |
| `disableHwidCheck` | Skip the HWID device limit check. The device is still recorded |
| `additionalExtendedClientsRegex` | `User-Agent` regular expressions that make a client "extended", see [below](#extended-clients) |
| `encryption` | Encrypt the response, see [below](#encryption) |
| `excludeHostsByTags` | Drop hosts with these tags. Tags use `A-Z`, `0-9`, `_` and `:`, up to 36 characters |
| `respondWithRemarks` | Return entries with these remarks instead of servers, for example an "update your app" message |

:::note[respondWithRemarks]
Works only when the subscription setting "Show custom remarks" (`isShowCustomRemarks`) is on. Without it the client gets an empty subscription. Remarks can use [variables](../template-variables/).
:::

If the user belongs to an external squad with its own template and the rule has no `subscriptionTemplate`, the panel uses the squad's template.

## Client type in the path

A link can name its type explicitly: `/api/sub/<shortUuid>/<type>`. The rules are then skipped.

| Path | Response |
| :--- | :--- |
| `json`, `v2ray-json` | `XRAY_JSON` |
| `mihomo` | `MIHOMO` |
| `stash` | `STASH` |
| `clash` | `CLASH` |
| `singbox` | `SINGBOX` |
| anything else | `BLOCK` |

`settings.disableSubscriptionAccessByPath: true` turns such links off: any type in the path gets `403`.

## Extended clients

For an "extended" client the response includes the host's server description (`serverDescription`): as `meta.serverDescription` in Xray JSON and as an extra field in links and Mihomo. A client is extended when its `User-Agent` starts with `FlClash X/`, `FlClashX/`, `Flowvy/`, `prizrak-box/`, `koala-clash/`, `Happ/` or `INCY/`. Add your own with `additionalExtendedClientsRegex`.

## JSON instead of base64

With the subscription setting "Serve JSON at the base subscription path" (`serveJsonAtBaseSubscription`) on, a rule answering `XRAY_BASE64` returns Xray JSON to clients that understand it: `Streisand`, `Happ/`, `INCY/`, `ktor-client`, `V2Box`, `io.github.saeeddev94.xray/`, `v2rayNG/`, `v2rayN/`, `v2plus/`. `ignoreServeJsonAtBaseSubscription` turns this off for one rule.

## Encryption

```json
"encryption": { "method": "age1", "key": "age1...recipient_public_key" }
```

The response is encrypted with [age](https://age-encryption.org) and returned as ASCII-armored text (`-----BEGIN AGE ENCRYPTED FILE-----`). `key` is the recipient's public key: `age1…` for `method: "age1"` or a post-quantum `age1pq1…` for `method: "age1pq1"`. Only a client holding the matching secret key can read the response. An invalid key produces an empty response.

## Examples

### Block an app

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

### A message instead of servers

Needs "Show custom remarks" on.

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
    "respondWithRemarks": ["Please switch to Happ", "Days left: {{DAYS_LEFT}}"]
  }
}
```

### Add a header for a client

For example, to pass the `providerid` header to Happ.

If a rule for Happ already exists in the list, no need to create a new one. Add the `headers` block inside `responseModifications` of that rule:

```json
"headers": [
  { "key": "providerid", "value": "12345" }
]
```

If there is no rule for Happ yet, create the whole rule:

```json
{
  "name": "Happ with ProviderID",
  "enabled": true,
  "operator": "AND",
  "conditions": [
    { "headerName": "user-agent", "operator": "STARTS_WITH", "value": "Happ/", "caseSensitive": false }
  ],
  "responseType": "XRAY_JSON",
  "responseModifications": {
    "headers": [
      { "key": "providerid", "value": "12345" }
    ]
  }
}
```

If the header needs to override default subscription headers (such as `content-disposition`), add `"applyHeadersToEnd": true` alongside. Header values support [template variables](../template-variables/).

### A separate template for one user

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

Put per-user rules above the general ones, or a `User-Agent` rule will match first.

## Default rules

| Rule | Condition | Response |
| :--- | :--- | :--- |
| Browser Subscription | `accept` contains `text/html` | `BROWSER` |
| Mihomo Clients | `user-agent` ~ `^(?:flclash\|rabbit\|flowvy\|murge\|mihomo\|prizrak-box\|koala-clash\|clash(?:-verge\|-nyanpasu\|x meta\|[-.]?meta))` | `MIHOMO` |
| Stash (iOS, macOS) | `user-agent` ~ `^stash` | `STASH` |
| Sing-box clients | `user-agent` ~ `^sfa\|sfi\|sfm\|sft\|karing\|singbox` | `SINGBOX` |
| Clash Core Clients | `user-agent` ~ `^clash` | `CLASH` |
| Fallback Base64 | no conditions | `XRAY_BASE64` |

The expressions in the table are case-insensitive. Do not delete or disable "Browser Subscription" and "Fallback Base64": without the first the subscription page stops working, without the second clients with an unknown `User-Agent` get `403`.

## Testing rules

The rules editor has a "Response rules debugger". It shows which rule matches your browser's headers and gives a cURL command carrying the current rules. Change the headers in that command to test any client without touching a real subscription. The rule matched by each real request appears in the "SRH Inspector" under Tools.
