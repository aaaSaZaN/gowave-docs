---
title: Panel and node on one server
description: Sharing port 443 between the panel and Xray with ssl_preread in Nginx.
sidebar:
  order: 4
---

The panel and node can run on the same server. The panel and Xray both need port 443. Nginx accepts the connection, reads the domain name from the TLS ClientHello (SNI) without decrypting anything, and uses it to decide where the connection goes:

```text
client :443 ── Nginx stream (ssl_preread)
                 ├─ SNI = panel.example.com → Nginx http 127.0.0.1:8443 → panel 127.0.0.1:3000
                 └─ any other SNI           → Xray 127.0.0.1:9443 (REALITY)
```

So that the panel and Xray see the real client IP instead of `127.0.0.1`, Nginx prepends a PROXY protocol header to the connection. Both sides accept it.

Replace `panel.example.com` with the panel domain in every example.

## Requirements

- Nginx with the `stream` and `ssl_preread` modules. To check:

  ```bash
  nginx -V 2>&1 | grep -o 'with-stream_ssl_preread_module'
  ```

  Debian / Ubuntu:

  ```bash
  apt update
  apt install nginx-full
  ```

  RHEL-like:

  ```bash
  dnf install nginx nginx-mod-stream
  ```

  Make sure the dynamic `stream` module is loaded by the distribution's module includes in `nginx.conf`.
- The panel on `127.0.0.1:3000`, installed with [systemd](../../systemd/) or [Docker](../../docker/).
- Port 443 free; for HTTP-01, port 80 must also be open and free.

## 1. Panel certificate

Run these commands as root. Replace `panel.example.com` with the panel domain. DNS-01 verifies ownership through a TXT record and does not require inbound ports 80 or 443.

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
    --cert-name panel.example.com -d panel.example.com
```

### Manual DNS-01

If your provider has no API plugin, install `certbot` with `apt install certbot` or `dnf install certbot` (with EPEL enabled) and run:

```bash
certbot certonly --manual --preferred-challenges dns --cert-name panel.example.com -d panel.example.com
```

Certbot prints the TXT record name `_acme-challenge.panel.example.com` and its value. Add the record in your DNS provider's control panel, wait until it is publicly visible, then press Enter in Certbot. Remove the record after verification. Without authentication hooks, this method requires repeating the manual challenge for each renewal.

### Alternative: HTTP-01

The standard method remains available. Point the domain's A/AAAA records at this server, open port 80/TCP in the firewall and make sure it is free:

```bash
ss -ltnp 'sport = :80'
certbot certonly --standalone --preferred-challenges http --cert-name panel.example.com -d panel.example.com
```

Disable the default Nginx site and any other configuration that listens on port 80. Certbot temporarily binds that port to complete the challenge. The configs below serve HTTPS only.

### Renewal

The certificate files are `/etc/letsencrypt/live/panel.example.com/fullchain.pem` and `privkey.pem`. After renewal, reload Nginx with a deploy hook:

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

## 2. Routing by SNI

The `stream` block must sit at the top level of `nginx.conf`, next to `http`, not inside it. Files in `conf.d/` are included inside `http`, so the block cannot go there. Create `/etc/nginx/stream.conf`:

```nginx
stream {
    map $ssl_preread_server_name $sni_backend {
        panel.example.com  127.0.0.1:8443;
        default            127.0.0.1:9443;
    }

    server {
        listen 443;
        listen [::]:443;
        ssl_preread on;
        proxy_pass $sni_backend;
        proxy_protocol on;
    }
}
```

Include it at the end of `/etc/nginx/nginx.conf`, after the closing brace of the `http` block:

```nginx
include /etc/nginx/stream.conf;
```

Connections without SNI (scanners hitting the IP) fall into `default`, so they go to Xray, and REALITY serves them the site from `target`.

## 3. Panel behind the stream block

`/etc/nginx/conf.d/gowave.conf`. The server listens only on `127.0.0.1:8443` and expects PROXY protocol from the `stream` block:

```nginx
map $http_upgrade $gowave_connection_upgrade {
    default upgrade;
    "" close;
}

server {
    listen 127.0.0.1:8443 ssl proxy_protocol;
    http2 on;
    server_name panel.example.com;

    # The real client IP comes from PROXY protocol
    set_real_ip_from 127.0.0.1;
    real_ip_header proxy_protocol;

    ssl_certificate /etc/letsencrypt/live/panel.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/panel.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;
    ssl_session_tickets off;

    server_tokens off;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    if ($host != "panel.example.com") {
        return 421;
    }

    error_log /var/log/nginx/gowave.error.log;

    client_max_body_size 50M;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 256;
    gzip_types application/javascript application/json application/wasm image/svg+xml text/css text/plain;

    location / {
        proxy_http_version 1.1;
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $gowave_connection_upgrade;
    }
}
```

`http2 on` requires Nginx 1.25.1 or newer; on older versions replace it and the `listen` line with `listen 127.0.0.1:8443 ssl http2 proxy_protocol;`.

```bash
nginx -t && systemctl reload nginx
```

Leave out the `listen 443 ... default_server` with `ssl_reject_handshake` from the [regular Nginx setup](../nginx/): port 443 belongs to the `stream` block. `nginx -t` accepts such a configuration, but Nginx then fails to start with `bind() to 0.0.0.0:443 failed (98: Address in use)`.

## 4. Node

Port `3000` is taken by the panel, so the Go node needs another management port, for example `2222`. The installer is downloaded in full first, so you can read it before running it:

```bash
curl -fsSLo /tmp/remnanode-install.sh https://raw.githubusercontent.com/aaaSaZaN/remnanode-go/main/install.sh
sudo NODE_PORT=2222 sh /tmp/remnanode-install.sh
```

In the panel, add the node with this server's IP and port `2222`.

## 5. Inbound in the config profile

Xray listens only on `127.0.0.1:9443` and accepts PROXY protocol. An example inbound for the config profile in the panel:

```json
{
  "tag": "VLESS_REALITY",
  "listen": "127.0.0.1",
  "port": 9443,
  "protocol": "vless",
  "settings": {
    "clients": [],
    "decryption": "none"
  },
  "streamSettings": {
    "network": "tcp",
    "security": "reality",
    "realitySettings": {
      "target": "www.example.com:443",
      "serverNames": ["www.example.com"],
      "privateKey": "<private key from xray x25519>",
      "shortIds": [""]
    },
    "sockopt": {
      "acceptProxyProtocol": true
    }
  }
}
```

Replace `www.example.com` with the site for REALITY. It must differ from the panel domain, or Nginx will send those clients to the panel.

In the host for this inbound set port **443**. Clients connect to Nginx; `9443` is an internal port that is not reachable from outside.

## Common mistakes

- **The `stream` block inside `http` or in `conf.d/`.** `nginx -t` reports `"stream" directive is not allowed here`.
- **PROXY protocol enabled in only some places.** `proxy_protocol on` in `stream` requires `proxy_protocol` in the panel's `listen` and `acceptProxyProtocol` in Xray. To go without it, remove it in all three places; the panel will then see `127.0.0.1` instead of client IPs.
- **The panel on `listen 443`.** The panel server must listen on `127.0.0.1:8443`. Port 443 belongs only to the `stream` block.
- **Port `9443` in the host.** Clients cannot connect: only 443 is open from outside.
- **The node on port `3000`.** The panel holds that port, and the node fails with `Address already in use`.
- **Port 80 in use.** `certbot --standalone` reports `Could not bind TCP port 80`. Usually the stock Nginx `default` site or a leftover `server` with `listen 80` holds it. Check with `ss -ltnp 'sport = :80'`.
- **No Nginx reload hook.** `certbot renew` succeeds, but after the certificate expires the panel starts serving an expired certificate.

## Subscription page on the same server

Issue a certificate for its domain with the same command as in step 1. Add the domain to the `map` with the same `127.0.0.1:8443` address, plus a separate `server` with `listen 127.0.0.1:8443 ssl proxy_protocol` and its own `server_name`. The page itself is covered in [Subscription page](../../subscription-page/).
