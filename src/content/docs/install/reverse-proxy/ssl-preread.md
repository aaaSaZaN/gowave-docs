---
title: Панель и нода на одном сервере
description: Базовый пример разделения порта 443 между панелью и Xray через ssl_preread в Nginx.
sidebar:
  order: 4
---

:::caution[Не поддерживается]
Панель и нода на одном сервере официально не поддерживаются, установщики так не ставят. Ниже - проверенная отправная точка для ручной настройки, а не готовое решение. Всё, что вы меняете дальше, остаётся на вас.
:::

Панели и Xray нужен один и тот же порт 443. Nginx принимает соединение, читает имя домена из TLS ClientHello (SNI) без расшифровки и по нему решает, куда отдать соединение:

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

  В Debian и Ubuntu модуль `stream` ставится отдельным пакетом: `apt install libnginx-mod-stream`.
- Панель на `127.0.0.1:3000`. В [установщике](../../installer/#свой-reverse-proxy) выберите «Не настраивать: свой reverse proxy» или поставьте панель [вручную](../../systemd/).
- Порт 443 свободен: Caddy и сайт `gowave.conf` от установщика удалите.

## 1. Сертификат панели

Порт 80 остаётся за обычным `http` Nginx, поэтому сертификат выпускается через webroot, и продление работает без остановки Nginx. Файл `/etc/nginx/conf.d/gowave-acme.conf`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name panel.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}
```

```bash
mkdir -p /var/www/letsencrypt
nginx -t && systemctl reload nginx
certbot certonly --webroot -w /var/www/letsencrypt -d panel.example.com
```

## 2. Разбор по SNI

Блок `stream` должен лежать на верхнем уровне `nginx.conf`, рядом с `http`, а не внутри него. Файлы из `conf.d/` подключаются внутри `http`, поэтому туда этот блок класть нельзя. Создайте `/etc/nginx/stream.conf`:

```nginx
stream {
    map $ssl_preread_server_name $sni_backend {
        panel.example.com  panel;
        default            xray;
    }

    upstream panel { server 127.0.0.1:8443; }
    upstream xray  { server 127.0.0.1:9443; }

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
map $http_upgrade $connection_upgrade {
    default upgrade;
    "" close;
}

upstream gowave {
    server 127.0.0.1:3000;
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

    client_max_body_size 50M;

    location / {
        proxy_http_version 1.1;
        proxy_pass http://gowave;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }
}
```

```bash
nginx -t && systemctl reload nginx
```

`listen 443 ... default_server` с `ssl_reject_handshake` из [обычной настройки Nginx](../nginx/) здесь не нужен: порт 443 занят блоком `stream`. `nginx -t` такую конфигурацию пропустит, но при запуске Nginx упадёт с `bind() to 0.0.0.0:443 failed (98: Address in use)`.

## 4. Нода

Порт `3000` уже занят панелью, поэтому Go-ноде нужен другой порт управления, например `2222`:

```bash
curl -fsSL https://raw.githubusercontent.com/aaaSaZaN/remnanode-go/main/install.sh | sudo NODE_PORT=2222 sh
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
- **Сертификат через `--standalone`.** Продление не пройдёт, пока Nginx держит порт 80. Используйте webroot, как в первом шаге.

## Страница подписки на этом же сервере

Добавьте её домен в `map` с тем же значением `panel` и отдельный `server` с `listen 127.0.0.1:8443 ssl proxy_protocol` и своим `server_name`. Сама страница описана в разделе [Страница подписки](../../subscription-page/).
