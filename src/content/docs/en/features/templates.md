---
title: Xray JSON templates
description: How the Xray JSON subscription is built, host injection with the remnawave block, Mihomo and sing-box templates, the host mapper.
sidebar:
  order: 10
---

Subscription templates live on the templates page of the Subscription section. Each format (Xray JSON, Mihomo, Stash, Clash, sing-box) can have several templates: one default, the others picked by [response rules](../subscription-rules/) via `subscriptionTemplate` or by external squads.

## How Xray JSON is built

An Xray JSON template is a regular Xray config: `log`, `dns`, `inbounds`, `routing`, `outbounds` and the rest. The subscription is a list of such configs, one per host of the user:

1. The template is chosen: the host's own template if it has one, otherwise the main one. A rule with `ignoreHostXrayJsonTemplate` always uses the main one.
2. An outbound tagged `proxy` is built from the host and placed **first** in `outbounds`, before the template's outbounds.
3. `remarks` is set to the host remark. [Extended clients](../subscription-rules/#extended-clients) also get `meta.serverDescription`.

Hidden hosts and hosts with Xray JSON excluded from their subscription types are skipped.

That is why routing in the template points at the `proxy` tag:

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

## The `remnawave` block: several hosts in one config

With a `remnawave` object in the template, the panel builds the config differently: `outbounds` get the hosts you select. This is how balancers, backup servers and chains are made. The `remnawave` block itself is removed from the response.

```json
{
  "remnawave": {
    "addVirtualHostAsOutbound": true,
    "injectHosts": [
      {
        "selector": { "type": "remarkRegex", "pattern": "^Backup" },
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

A config is still built for every host; the host a config is built for is called "current" below.

| Field | Description |
| :--- | :--- |
| `addVirtualHostAsOutbound` | `true`: the current host is added with the `proxy` tag |
| `injectHosts` | List of selections, each adding the matched hosts as outbounds |

The injected outbounds go before the template's outbounds, in selection order.

:::caution[An empty block drops the host]
If the `remnawave` block is present but `addVirtualHostAsOutbound` is off and `injectHosts` is empty, no config is built for the host and it disappears from the subscription.
:::

### Selecting hosts

| Field | Description |
| :--- | :--- |
| `selector` | Which hosts to pick, see the table below. Required |
| `selectFrom` | Where to pick from: `HIDDEN` (default, hidden hosts only), `NOT_HIDDEN` or `ALL`. The current host is never included |
| `tagPrefix` | Outbound tags: `<prefix>`, `<prefix>-2`, `<prefix>-3` and so on. Default `proxy` |
| `useHostRemarkAsTag` | `true`: the host remark becomes the tag |
| `useHostTagAsTag` | `true`: the host's first tag becomes the tag, or its remark if it has no tags |

If both `useHostRemarkAsTag` and `useHostTagAsTag` are set, the first one wins. `tagPrefix` applies when both are off.

| `selector.type` | Parameters | Which hosts |
| :--- | :--- | :--- |
| `uuids` | `values`: list of UUIDs | Hosts with these UUIDs, in list order |
| `remarkRegex` | `pattern` | The remark matches the expression |
| `tagRegex` | `pattern` | At least one host tag matches the expression |
| `sameTagAsRecipient` | none | Hosts sharing a tag with the current host |

Regular expressions use RE2 syntax: no lookahead, lookbehind or backreferences. An invalid expression matches nothing.

Hidden hosts work well as spare parts: users do not see them as separate servers, but they are injected into the configs of visible hosts. Give selections their own `tagPrefix` so their tags do not clash with the current host's `proxy`.

## Mihomo and Stash templates

Servers are appended to the template's `proxies`, and their names (host remarks) are added to every group in `proxy-groups`. Hosts on the `kcp` transport are skipped, and for Stash so are `xhttp` hosts.

`remnawave` blocks control this:

| Where | Field | What it does |
| :--- | :--- | :--- |
| Template root (Mihomo) | `includeHiddenHosts: true` | Include hidden hosts too |
| Group in `proxy-groups` | `include-proxies: false` | Do not add servers to this group |
| Group in `proxy-groups` | `select-random-proxy: true` | Add one random server |
| Group in `proxy-groups` | `shuffle-proxies-order: true` | Add all servers in random order |
| Provider in `proxy-providers` (Mihomo) | `include-proxies: true` | Put all servers into the provider's `payload` |

```yaml
proxy-groups:
  - name: Auto
    type: url-test
    url: https://www.gstatic.com/generate_204
    interval: 300
  - name: Backup
    type: select
    proxies: [DIRECT]
    remnawave:
      shuffle-proxies-order: true
```

## sing-box template

Servers are added to `outbounds`, and their tags are added to every outbound of type `selector` and `urltest`. To leave one of them untouched, give it `"remnawave": { "includeProxies": false }`.

## Host mapper

Every host has a mapper field: operations that change the part of the subscription already built for that host. Operations are set per format: `xrayJson`, `mihomo`, `singbox`, `base64`.

```json
{
  "xrayJson": [
    { "op": "set", "to": "streamSettings.sockopt.tcpFastOpen", "value": true },
    { "op": "copy", "from": "$host.metadata.remark", "to": "tag" },
    { "op": "unset", "to": "mux" }
  ]
}
```

| `op` | Fields | Action |
| :--- | :--- | :--- |
| `set` | `to`, `value` | Write a value at a path |
| `copy` | `from`, `to` | Copy a value from the inbound or the host |
| `unset` | `to` | Remove a value |

- `to` is a dot-separated path inside the built object: the Xray outbound, the Mihomo proxy, the sing-box outbound.
- `from` without a prefix is a path inside the source inbound from the config profile; with the `$host.` prefix it reads a host field. Available: `address`, `port`, `protocol`, `finalRemark`, `mux`, `security`, `securityOptions`, `transport`, `transportOptions`, `protocolOptions`, `metadata.inboundTag`, `metadata.remark`, `metadata.tags`, `clientOverrides.serverDescription`, `streamOverrides.finalMask`, `streamOverrides.sockopt` and fields nested in them.
- An operation is skipped if its source is missing or the path runs through a plain value (a string or a number).
- In `base64` you can change link parameters (`to` is the parameter name) and the link itself through `$link.address`, `$link.port`, `$link.password`, `$link.method`, `$link.remark`.
