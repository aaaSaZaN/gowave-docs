---
title: Caddy
description: HTTPS для панели через Caddy.
sidebar:
  order: 2
---

Сертификат выпускается и продлевается автоматически. Добавьте в `/etc/caddy/Caddyfile`:

```text
panel.yourdomain.com {
    encode zstd gzip
    reverse_proxy 127.0.0.1:3000
}
```

```bash
systemctl reload caddy
```
