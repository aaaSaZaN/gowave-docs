---
title: Nginx
description: HTTPS для панели через Nginx и Certbot.
sidebar:
  order: 3
---

## Сертификат

Выполняйте команды от root. Замените `panel.yourdomain.com` на домен панели. DNS-01 подтверждает владение доменом через TXT-запись и не требует входящих соединений на порты 80 и 443.

### DNS-01 с автоматическим продлением

Пример для домена с DNS в Cloudflare. Для другого провайдера установите его [DNS-плагин Certbot](https://eff-certbot.readthedocs.io/en/stable/using.html#dns-plugins) или используйте ручной способ ниже.

Debian / Ubuntu:

```bash
apt update
apt install certbot python3-certbot-dns-cloudflare
```

RHEL-like (предварительно подключите [EPEL](https://docs.fedoraproject.org/en-US/epel/getting-started/)):

```bash
dnf install certbot python3-certbot-dns-cloudflare
```

Создайте API-токен с правом `Zone:DNS:Edit`, ограниченным зоной нужного домена. Сохраните его в файле, доступном только root, как описано в [документации плагина](https://certbot-dns-cloudflare.readthedocs.io/en/stable/):

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

### Ручной DNS-01

Если у провайдера нет API-плагина, установите `certbot` через `apt install certbot` или `dnf install certbot` (с подключённым EPEL) и выполните:

```bash
certbot certonly --manual --preferred-challenges dns --cert-name panel.yourdomain.com -d panel.yourdomain.com
```

Certbot покажет имя TXT-записи `_acme-challenge.panel.yourdomain.com` и её значение. Добавьте запись у DNS-провайдера, дождитесь её появления в публичном DNS и нажмите Enter в Certbot. После проверки запись можно удалить. Без authentication hooks при каждом продлении потребуется повторять ручную проверку.

### Альтернатива: HTTP-01

Обычный способ также доступен. Направьте A/AAAA-записи домена на этот сервер, откройте порт 80/TCP в файрволе и проверьте, что он свободен:

```bash
ss -ltnp 'sport = :80'
certbot certonly --standalone --preferred-challenges http --cert-name panel.yourdomain.com -d panel.yourdomain.com
```

Отключите стандартный сайт Nginx и другие конфиги, которые слушают порт 80. Certbot временно занимает этот порт для проверки. Конфиги ниже обслуживают только HTTPS.

### Продление

Файлы сертификата: `/etc/letsencrypt/live/panel.yourdomain.com/fullchain.pem` и `privkey.pem`. После продления перезагружайте Nginx через deploy hook:

```bash
install -d /etc/letsencrypt/renewal-hooks/deploy
cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh <<'EOF'
#!/bin/sh
nginx -t && systemctl reload nginx
EOF
chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

Для автоматического DNS-01 и HTTP-01 включите таймер установленного пакета (`certbot.timer` в Debian/Ubuntu, `certbot-renew.timer` в EPEL), затем проверьте продление после настройки Nginx:

```bash
systemctl enable --now certbot.timer
certbot renew --dry-run
```

В RHEL-like используйте `systemctl enable --now certbot-renew.timer`. Плагин Cloudflare повторно использует сохранённый файл токена — оставьте его на сервере.

## Конфигурация Nginx

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

# Сброс рукопожатия при обращении по IP
server {
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    server_name _;
    ssl_reject_handshake on;
}
```

`ssl_reject_handshake` работает в Nginx 1.19.4 и новее, `http2 on` - в 1.25.1 и новее (на старых версиях пишите `listen 443 ssl http2;`).

```bash
nginx -t && systemctl reload nginx
```

`application/wasm` в `gzip_types` нужен для валидатора Xray в редакторе профилей: это Xray-core, собранный в WebAssembly (~60 МБ). Он скачивается и работает только в браузере администратора при открытии редактора, в памяти сервера не держится. Панель уже отдаёт его сжатым (~12 МБ), а Nginx не сжимает такие ответы повторно.
