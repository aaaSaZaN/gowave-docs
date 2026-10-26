---
title: Nginx
description: HTTPS for the panel with Nginx and Certbot.
sidebar:
  order: 3
---

## Certificate

Run these commands as root. Replace `panel.yourdomain.com` with the panel domain. DNS-01 verifies ownership through a TXT record and does not require inbound ports 80 or 443.

### DNS-01 with automatic renewal

The example uses Cloudflare DNS. For another provider, install its [Certbot DNS plugin](https://eff-certbot.readthedocs.io/en/stable/using.html#dns-plugins) or use the manual method below.

Debian / Ubuntu:

```bash
apt update
apt install certbot python3-certbot-dns-cloudflare
```

RHEL-like (enable [EPEL](https://docs.fedoraproject.org/en-US/epel/getting-started/) first):

```bash
dnf install certbot python3-certbot-dns-cloudflare
```

Create an API token with `Zone:DNS:Edit` permission limited to the domain zone. Store it in a file readable only by root, as described in the [plugin documentation](https://certbot-dns-cloudflare.readthedocs.io/en/stable/):

```bash
install -d -m 700 /root/.secrets/certbot
install -m 600 /dev/null /root/.secrets/certbot/cloudflare.ini
nano /root/.secrets/certbot/cloudflare.ini
```

```ini
dns_cloudflare_api_token = YOUR_CLOUDFLARE_API_TOKEN
```

```bash
certbot certonly --dns-cloudflare \
    --dns-cloudflare-credentials /root/.secrets/certbot/cloudflare.ini \
    --dns-cloudflare-propagation-seconds 60 \
    --cert-name panel.yourdomain.com -d panel.yourdomain.com
```

### Manual DNS-01

If your provider has no API plugin, install `certbot` with `apt install certbot` or `dnf install certbot` (with EPEL enabled) and run:

```bash
certbot certonly --manual --preferred-challenges dns --cert-name panel.yourdomain.com -d panel.yourdomain.com
```

Certbot prints the TXT record name `_acme-challenge.panel.yourdomain.com` and its value. Add the record in your DNS provider's control panel, wait until it is publicly visible, then press Enter in Certbot. Remove the record after verification. Without authentication hooks, this method requires repeating the manual challenge for each renewal.

### Alternative: HTTP-01

The standard method remains available. Point the domain's A/AAAA records at this server, open port 80/TCP in the firewall and make sure it is free:

```bash
ss -ltnp 'sport = :80'
certbot certonly --standalone --preferred-challenges http --cert-name panel.yourdomain.com -d panel.yourdomain.com
```

Disable the default Nginx site and any other configuration that listens on port 80. Certbot temporarily binds that port to complete the challenge. The configs below serve HTTPS only.

### Renewal

The certificate files are `/etc/letsencrypt/live/panel.yourdomain.com/fullchain.pem` and `privkey.pem`. After renewal, reload Nginx with a deploy hook:

```bash
install -d /etc/letsencrypt/renewal-hooks/deploy
cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh <<'EOF'
#!/bin/sh
nginx -t && systemctl reload nginx
EOF
chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

For automatic DNS-01 and HTTP-01, enable the installed package's renewal timer (`certbot.timer` on Debian/Ubuntu, `certbot-renew.timer` on EPEL), then test renewal after Nginx is configured:

```bash
systemctl enable --now certbot.timer
certbot renew --dry-run
```

On RHEL-like use `systemctl enable --now certbot-renew.timer`. The Cloudflare plugin reuses the saved token file; keep it on the server.

## Nginx configuration

`/etc/nginx/conf.d/gowave.conf`:

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    "" close;
}

server {
    server_name panel.yourdomain.com;
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;

    server_tokens off;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    if ($host != "panel.yourdomain.com") {
        return 421;
    }

    error_log /var/log/nginx/gowave.error.log;

    client_max_body_size 50M;

    location / {
        proxy_http_version 1.1;
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
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

`application/wasm` in `gzip_types` covers the Xray validator in the profile editor: Xray-core compiled to WebAssembly (~60 MB). It is downloaded and run only in the administrator's browser when the editor opens; the server does not keep it in memory. The panel already sends it compressed (~12 MB), and Nginx does not compress such responses again.
