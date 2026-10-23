---
title: Caddy
description: HTTPS for the panel with Caddy.
sidebar:
  order: 2
---

Certificates are issued and renewed automatically. Add to `/etc/caddy/Caddyfile`:

```text
panel.yourdomain.com {
    encode zstd gzip
    reverse_proxy 127.0.0.1:3000
}
```

```bash
systemctl reload caddy
```

`encode` also compresses `application/wasm` (Caddy 2.7+). The panel already sends the Xray validator for the profile editor (~60 MB of WebAssembly) compressed, about 12 MB. It is downloaded and run only in the administrator's browser.
