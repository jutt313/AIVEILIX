#!/usr/bin/env bash
set -euo pipefail

DATA_DISK_DEVICE="/dev/disk/by-id/google-aiveilix-data"
DATA_DIR="/opt/aiveilix"

apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
  curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
fi

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

if ! blkid "$DATA_DISK_DEVICE"; then
  mkfs.ext4 -F "$DATA_DISK_DEVICE"
fi

mkdir -p "$DATA_DIR"
if ! grep -q "$DATA_DISK_DEVICE" /etc/fstab; then
  echo "$DATA_DISK_DEVICE $DATA_DIR ext4 discard,defaults,nofail 0 2" >> /etc/fstab
fi
mount -a

mkdir -p "$DATA_DIR/qdrant_storage" "$DATA_DIR/valkey_data"

cat > "$DATA_DIR/docker-compose.yml" <<'YAML'
services:
  qdrant:
    image: qdrant/qdrant:v1.15.4
    restart: unless-stopped
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      QDRANT__SERVICE__HTTP_PORT: "6333"

  valkey:
    image: valkey/valkey:8.1
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: ["valkey-server", "--appendonly", "yes", "--save", "60", "1"]
    volumes:
      - ./valkey_data:/data
YAML

cat > /etc/systemd/system/aiveilix-vector-cache.service <<EOF
[Unit]
Description=AIveilix Qdrant and Valkey
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DATA_DIR
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now aiveilix-vector-cache.service
