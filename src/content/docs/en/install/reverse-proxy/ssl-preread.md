---
title: Panel and node on one server
description: A basic example of sharing port 443 between the panel and Xray with ssl_preread in Nginx.
sidebar:
  order: 4
---

:::caution[Not recommended]
Running the panel and a node on the same server is not recommended, and the installers do not set it up. What follows is a tested starting point for a manual setup, not a finished solution. Anything you change from here, and getting the setup right, is on you.
:::

The panel and Xray both need port 443. Nginx accepts the connection, reads the domain name from the TLS ClientHello (SNI) without decrypting anything, and uses it to decide where the connection goes:

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

  On Debian and Ubuntu the `stream` module is a separate package: `apt install libnginx-mod-stream`.
- The panel on `127.0.0.1:3000`. In the [installer](../../installer/#your-own-reverse-proxy) pick "Skip: I will use my own reverse proxy", or install the panel [manually](../../systemd/).
- Ports 80 and 443 free.

## 1. Panel certificate

Nginx does not listen on port 80 in this setup, so the port goes to certbot. In `--standalone` mode certbot starts a temporary server on port 80, passes the challenge, and releases the port right away. Port 80 must be open in the firewall.

Check that port 80 is free. The output should contain nothing but the header line:

```bash
ss -ltnp 'sport = :80'
```

```bash
certbot certonly --standalone -d panel.example.com
```

The certificate lands in `/etc/letsencrypt/live/panel.example.com/` (`fullchain.pem` and `privkey.pem`), the paths used in step 3. The directory is named after the first `-d` domain.

`certonly` only issues the certificate and leaves the Nginx configuration alone. Nginx has to be reloaded after a renewal, otherwise it keeps serving the old certificate from memory. Certbot runs the scripts in `renewal-hooks/deploy/` after every successful renewal:

```bash
cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh <<'EOF'
#!/bin/sh
systemctl reload nginx
EOF
chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

There is no `http://` to `https://` redirect here: `http://panel.example.com` does not open. If you would rather not open port 80 at all, issue the certificate through DNS-01: a certbot plugin for your DNS provider (for example `certbot-dns-cloudflare`) or acme.sh.

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
- **No Nginx reload hook.** `certbot renew` succeeds, but 90 days after issuance the panel starts serving an expired certificate.

## Subscription page on the same server

Issue a certificate for its domain with the same command as in step 1. Add the domain to the `map` with the same `127.0.0.1:8443` address, plus a separate `server` with `listen 127.0.0.1:8443 ssl proxy_protocol` and its own `server_name`. The page itself is covered in [Subscription page](../../subscription-page/).
