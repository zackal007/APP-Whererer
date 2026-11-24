#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq tinyproxy > /dev/null
CONF=/etc/tinyproxy/tinyproxy.conf
sed -i 's/^Port .*/Port 443/' $CONF
grep -q '^Port 443' $CONF || echo 'Port 443' >> $CONF
sed -i '/^BasicAuth /d' $CONF
echo 'BasicAuth relayusr Rly-9f3kQ7xZ-2026' >> $CONF
sed -i 's/^Timeout .*/Timeout 120/' $CONF
grep -q '^Timeout 120' $CONF || echo 'Timeout 120' >> $CONF
systemctl enable tinyproxy > /dev/null 2>&1 || true
systemctl restart tinyproxy
sleep 1
systemctl is-active tinyproxy
ss -tlnp | grep 443 || netstat -tlnp | grep 443
echo RELAY_SETUP_DONE
