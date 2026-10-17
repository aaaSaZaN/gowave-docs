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
