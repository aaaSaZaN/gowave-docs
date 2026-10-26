---
title: Панель и нода на одном сервере
description: Разделение порта 443 между панелью и Xray через ssl_preread в Nginx.
sidebar:
  order: 4
---

Панель и нода могут работать на одном сервере. Панели и Xray нужен один и тот же порт 443. Nginx принимает соединение, читает имя домена из TLS ClientHello (SNI) без расшифровки и по нему решает, куда отдать соединение:

```text
клиент :443 ── Nginx stream (ssl_preread)
                 ├─ SNI = panel.example.com → Nginx http 127.0.0.1:8443 → панель 127.0.0.1:3000
                 └─ любой другой SNI        → Xray 127.0.0.1:9443 (REALITY)
```

Чтобы панель и Xray видели настоящий IP клиента, а не `127.0.0.1`, Nginx добавляет к соединению заголовок PROXY protocol, и обе стороны умеют его читать.

Во всех примерах замените `panel.example.com` на домен панели.

## Что нужно

- Nginx с модулями `stream` и `ssl_preread`. Проверка:

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

  Убедитесь, что динамический модуль `stream` загружается через штатные include модулей дистрибутива в `nginx.conf`.
- Панель на `127.0.0.1:3000`, установленная через [systemd](../../systemd/) или [Docker](../../docker/).
- Порт 443 свободен; для HTTP-01 также нужен открытый и свободный порт 80.

## 1. Сертификат панели

Выполняйте команды от root. Замените `panel.example.com` на домен панели. DNS-01 подтверждает владение доменом через TXT-запись и не требует входящих соединений на порты 80 и 443.

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
    --cert-name panel.example.com -d panel.example.com
```

### Ручной DNS-01

Если у провайдера нет API-плагина, установите `certbot` через `apt install certbot` или `dnf install certbot` (с подключённым EPEL) и выполните:

```bash
certbot certonly --manual --preferred-challenges dns --cert-name panel.example.com -d panel.example.com
```

Certbot покажет имя TXT-записи `_acme-challenge.panel.example.com` и её значение. Добавьте запись у DNS-провайдера, дождитесь её появления в публичном DNS и нажмите Enter в Certbot. После проверки запись можно удалить. Без authentication hooks при каждом продлении потребуется повторять ручную проверку.

### Альтернатива: HTTP-01

Обычный способ также доступен. Направьте A/AAAA-записи домена на этот сервер, откройте порт 80/TCP в файрволе и проверьте, что он свободен:

```bash
ss -ltnp 'sport = :80'
certbot certonly --standalone --preferred-challenges http --cert-name panel.example.com -d panel.example.com
```

Отключите стандартный сайт Nginx и другие конфиги, которые слушают порт 80. Certbot временно занимает этот порт для проверки. Конфиги ниже обслуживают только HTTPS.

### Продление

Файлы сертификата: `/etc/letsencrypt/live/panel.example.com/fullchain.pem` и `privkey.pem`. После продления перезагружайте Nginx через deploy hook:

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

## 2. Разбор по SNI

Блок `stream` должен лежать на верхнем уровне `nginx.conf`, рядом с `http`, а не внутри него. Файлы из `conf.d/` подключаются внутри `http`, поэтому туда этот блок класть нельзя. Создайте `/etc/nginx/stream.conf`:

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

И подключите его в конце `/etc/nginx/nginx.conf`, после закрывающей скобки блока `http`:

```nginx
include /etc/nginx/stream.conf;
```

Соединения без SNI (сканеры по IP) попадают в `default`, то есть в Xray, а REALITY отдаёт им сайт из `target`.

## 3. Панель за stream

Файл `/etc/nginx/conf.d/gowave.conf`. Сервер слушает только `127.0.0.1:8443` и ждёт PROXY protocol от блока `stream`:

```nginx
map $http_upgrade $gowave_connection_upgrade {
    default upgrade;
    "" close;
}

server {
    listen 127.0.0.1:8443 ssl proxy_protocol;
    http2 on;
    server_name panel.example.com;

    # Настоящий IP клиента берётся из PROXY protocol
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

`http2 on` требует Nginx 1.25.1 и новее; на старых версиях замените его и строку `listen` на `listen 127.0.0.1:8443 ssl http2 proxy_protocol;`.

```bash
nginx -t && systemctl reload nginx
```

`listen 443 ... default_server` с `ssl_reject_handshake` из [обычной настройки Nginx](../nginx/) здесь не нужен: порт 443 занят блоком `stream`. `nginx -t` такую конфигурацию пропустит, но при запуске Nginx упадёт с `bind() to 0.0.0.0:443 failed (98: Address in use)`.

## 4. Нода

Порт `3000` уже занят панелью, поэтому Go-ноде нужен другой порт управления, например `2222`. Установщик сначала скачивается целиком, его можно просмотреть перед запуском:

```bash
curl -fsSLo /tmp/remnanode-install.sh https://raw.githubusercontent.com/aaaSaZaN/remnanode-go/main/install.sh
sudo NODE_PORT=2222 sh /tmp/remnanode-install.sh
```

В панели добавьте ноду с IP этого сервера и портом `2222`.

## 5. Inbound в профиле конфигурации

Xray слушает только `127.0.0.1:9443` и принимает PROXY protocol. Пример inbound для профиля конфигурации в панели:

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
      "privateKey": "<приватный ключ из xray x25519>",
      "shortIds": [""]
    },
    "sockopt": {
      "acceptProxyProtocol": true
    }
  }
}
```

`www.example.com` замените на сайт для REALITY. Он не должен совпадать с доменом панели, иначе Nginx отправит клиентов в панель.

В хосте для этого inbound укажите порт **443**. Клиенты подключаются к Nginx, а `9443` - внутренний порт, снаружи он недоступен.

## Частые ошибки

- **Блок `stream` внутри `http` или в `conf.d/`.** `nginx -t` ответит `"stream" directive is not allowed here`.
- **PROXY protocol включён не везде.** `proxy_protocol on` в `stream` требует `proxy_protocol` в `listen` у панели и `acceptProxyProtocol` у Xray. Если хотите без него, уберите его во всех трёх местах. Тогда панель будет видеть `127.0.0.1` вместо IP клиентов.
- **Панель на `listen 443`.** Сервер панели должен слушать `127.0.0.1:8443`. Порт 443 принадлежит только блоку `stream`.
- **В хосте порт `9443`.** Клиенты не смогут подключиться: снаружи открыт только 443.
- **Нода на порту `3000`.** Порт занят панелью, нода не запустится с `Address already in use`.
- **Порт 80 занят.** `certbot --standalone` ответит `Could not bind TCP port 80`. Обычно его держит стандартный сайт Nginx `default` или оставшийся `server` с `listen 80`. Проверьте `ss -ltnp 'sport = :80'`.
- **Нет хука перезагрузки Nginx.** `certbot renew` проходит успешно, но после истечения срока сертификата панель начинает отдавать просроченный сертификат.

## Страница подписки на этом же сервере

Выпустите для её домена сертификат той же командой из первого шага. Добавьте домен в `map` с тем же адресом `127.0.0.1:8443` и отдельный `server` с `listen 127.0.0.1:8443 ssl proxy_protocol` и своим `server_name`. Сама страница описана в разделе [Страница подписки](../../subscription-page/).
