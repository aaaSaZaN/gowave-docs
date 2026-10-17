---
title: Nginx
description: HTTPS for the panel with Nginx and Certbot.
sidebar:
  order: 3
---

Certificate (port 80 must be free):

```bash
certbot certonly --standalone -d panel.yourdomain.com
```

`/etc/nginx/conf.d/gowave.conf`:

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    "" close;
}

upstream gowave {
    server 127.0.0.1:3000;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name panel.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    server_name panel.yourdomain.com;
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;

    client_max_body_size 50M;

    location / {
        proxy_http_version 1.1;
        proxy_pass http://gowave;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;
    ssl_session_tickets off;

    ssl_certificate /etc/letsencrypt/live/panel.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/panel.yourdomain.com/privkey.pem;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 256;
    gzip_types application/javascript application/json application/wasm image/svg+xml text/css text/plain;
}

# Reject TLS handshakes for requests by IP
server {
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    server_name _;
    ssl_reject_handshake on;
}
```

`ssl_reject_handshake` needs Nginx 1.19.4 or newer, `http2 on` needs 1.25.1 or newer (on older versions use `listen 443 ssl http2;`).

```bash
nginx -t && systemctl reload nginx
```
