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

`encode` сжимает и `application/wasm` (Caddy 2.7+). Валидатор Xray в редакторе профилей (~60 МБ WebAssembly) панель и так отдаёт сжатым, около 12 МБ. Он скачивается и работает только в браузере администратора.
