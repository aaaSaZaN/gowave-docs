---
title: Template variables
description: User variables in host remarks, custom remarks and response headers.
sidebar:
  order: 4
---

User data can be inserted into host remarks, custom remarks (for expired, disabled and limited users, for an empty host list and for an exceeded HWID limit), `respondWithRemarks` in [response rules](../subscription-rules/), custom response headers and the device limit message.

```text
🇩🇪 Germany · {{DAYS_LEFT}} days left · {{TRAFFIC_LEFT}}
```

An unknown variable is left in the text as is.

## Variables

| Variable | Value |
| :--- | :--- |
| `{{USERNAME}}` | Username |
| `{{ID}}` | Numeric ID |
| `{{SHORT_UUID}}` | Short UUID from the subscription link |
| `{{SUBSCRIPTION_URL}}` | Full subscription link |
| `{{EMAIL}}`, `{{TELEGRAM_ID}}`, `{{TAG}}`, `{{DESCRIPTION}}` | User fields, empty when not set |
| `{{STATUS}}` | Status: `Active`, `Expired`, `Disabled`, `Limited` |
| `{{DAYS_LEFT}}` | Days until the subscription ends, at least 0 |
| `{{EXPIRE_UNIX}}` | Expiry date, Unix time in seconds |
| `{{TRAFFIC_USED}}`, `{{TRAFFIC_LEFT}}`, `{{TOTAL_TRAFFIC}}` | Traffic in readable form: `1.23 GiB` |
| `{{TRAFFIC_USED_BYTES}}`, `{{TRAFFIC_LEFT_BYTES}}`, `{{TOTAL_TRAFFIC_BYTES}}` | The same in bytes |
| `{{LIFETIME_USED_BYTES}}` | All-time traffic, bytes |
| `{{RESET_STRATEGY}}` | Traffic reset: `NO_RESET`, `DAY`, `WEEK`, `MONTH`, `MONTH_ROLLING` |
| `{{LAST_TRAFFIC_RESET_AT}}`, `{{NEXT_TRAFFIC_RESET_AT}}` | Dates of the last and next traffic reset |
| `{{LAST_TRAFFIC_RESET_AT_UNIX}}`, `{{NEXT_TRAFFIC_RESET_AT_UNIX}}` | The same in Unix time, `0` when there is no date |
| `{{CREATED_AT_UNIX}}` | User creation date, Unix time |
| `{{SS_HWID_LIMIT}}` | Device limit: the user's own, otherwise the global one, otherwise `0` |

Without a traffic limit, `TRAFFIC_LEFT` and `TOTAL_TRAFFIC` are zero.

## Parameters

Parameters follow a colon: `{{VARIABLE:key=value|key=value}}`.

- **Custom labels for status and reset strategy:**

  ```text
  {{STATUS:ACTIVE=On|EXPIRED=Expired|DISABLED=Off|LIMITED=Over limit}}
  {{RESET_STRATEGY:MONTH=monthly|NO_RESET=never}}
  ```

  Values without a custom label print the standard one.

- **Date format** for `LAST_TRAFFIC_RESET_AT` and `NEXT_TRAFFIC_RESET_AT`, default `DD.MM.YYYY`:

  ```text
  Traffic resets {{NEXT_TRAFFIC_RESET_AT:format=MMM D, HH:mm}}
  ```

  Tokens as in dayjs: `YYYY`, `YY`, `MM`, `MMM`, `MMMM`, `DD`, `HH`, `mm`, `ss` and others. Month and weekday names are in English. Times are in UTC.

## Base64

A string starting with `rwEncodeBase64:` is encoded after substitution and printed as `base64:<encoded text>`. This is how text with line breaks and emoji is passed in headers, for example the `announce` header that Happ and other clients show.
