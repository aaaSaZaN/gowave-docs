---
title: Панель и нода на одном сервере
description: Базовый пример разделения порта 443 между панелью и Xray через ssl_preread в Nginx.
sidebar:
  order: 4
---

:::caution[Не рекомендуется]
Ставить панель и ноду на один сервер не рекомендуется, установщики так не ставят. Ниже - проверенная отправная точка для ручной настройки, а не готовое решение. Всё, что вы меняете дальше, и грамотность настройки остаются на вашей совести.
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
- Порты 80 и 443 свободны.

## 1. Сертификат панели

Nginx в этой схеме не слушает порт 80, поэтому порт отдаётся certbot. В режиме `--standalone` certbot сам поднимает временный сервер на порту 80, проходит проверку и сразу освобождает порт. Порт 80 должен быть открыт в файрволе.

Проверьте, что порт 80 свободен: кроме строки заголовка, вывод должен быть пустым.

```bash
ss -ltnp 'sport = :80'
```

```bash
certbot certonly --standalone -d panel.example.com
```

Сертификат ляжет в `/etc/letsencrypt/live/panel.example.com/` (`fullchain.pem` и `privkey.pem`), эти пути используются в шаге 3. Папка называется по первому домену из `-d`.

`certonly` только выпускает сертификат и не трогает конфигурацию Nginx. После продления Nginx нужно перезагрузить, иначе он продолжит отдавать старый сертификат из памяти. Certbot запускает скрипты из `renewal-hooks/deploy/` после каждого успешного продления:

```bash
cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh <<'EOF'
#!/bin/sh
systemctl reload nginx
EOF
chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

Редиректа с `http://` на `https://` здесь нет: `http://panel.example.com` не откроется. Если не хотите открывать порт 80 вовсе, выпускайте сертификат через DNS-01: плагин certbot для вашего DNS-провайдера (например, `certbot-dns-cloudflare`) или acme.sh.

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

    client_max_body_size 50M;

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
- **Нет хука перезагрузки Nginx.** `certbot renew` проходит успешно, но через 90 дней после выпуска панель начинает отдавать просроченный сертификат.

## Страница подписки на этом же сервере

Выпустите для её домена сертификат той же командой из первого шага. Добавьте домен в `map` с тем же адресом `127.0.0.1:8443` и отдельный `server` с `listen 127.0.0.1:8443 ssl proxy_protocol` и своим `server_name`. Сама страница описана в разделе [Страница подписки](../../subscription-page/).
