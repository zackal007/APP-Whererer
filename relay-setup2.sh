#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive
systemctl stop tinyproxy 2>/dev/null || true
systemctl disable tinyproxy 2>/dev/null || true
apt-get update -qq
apt-get install -y -qq certbot > /dev/null
HOST=49.235.152.94.sslip.io
certbot certonly --standalone -d $HOST --agree-tos --register-unsafely-without-email --non-interactive --http-01-port 80 || true
mkdir -p /etc/letsencrypt/live/relayhost
cp -L /etc/letsencrypt/live/$HOST/fullchain.pem /etc/letsencrypt/live/relayhost/fullchain.pem
cp -L /etc/letsencrypt/live/$HOST/privkey.pem /etc/letsencrypt/live/relayhost/privkey.pem
curl -fsSL https://raw.githubusercontent.com/zackal007/APP-Whererer/main/relay_server.py -o /usr/local/bin/relay_server.py
cat > /etc/systemd/system/wxrelay.service <<'UNIT'
[Unit]
Description=WeChat API relay
After=network.target
[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/relay_server.py
Restart=always
User=root
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable wxrelay > /dev/null 2>&1 || true
systemctl restart wxrelay
sleep 2
systemctl is-active wxrelay
ss -tlnp | grep 443 || true
echo RELAY2_SETUP_DONE
