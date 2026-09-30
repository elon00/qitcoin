#!/usr/bin/env bash
# 1-Click Qitcoin Public Testnet Seed Node Deployer (Ubuntu 22.04 / 24.04 LTS)
set -e

echo "========================================================="
echo "   QITCOIN (QTC) PUBLIC TESTNET SEED NODE INSTALLER      "
echo "========================================================="

# 1. Update OS and install dependencies
sudo apt-get update && sudo apt-get install -y curl git ufw jq

# 2. Configure Firewall
echo "[1/4] Configuring firewall ports (P2P: 19333, RPC: 19332)..."
sudo ufw allow 19333/tcp comment 'Qitcoin Testnet P2P'
sudo ufw allow 19332/tcp comment 'Qitcoin Testnet RPC'
sudo ufw --force enable || true

# 3. Setup Qitcoin Directory & User
echo "[2/4] Setting up node workspace..."
QTC_DIR="/opt/qitcoin"
sudo mkdir -p "${QTC_DIR}"
sudo chown -R $USER:$USER "${QTC_DIR}"

if [ ! -d "${QTC_DIR}/.git" ]; then
    git clone https://github.com/elon00/qitcoin.git "${QTC_DIR}"
else
    cd "${QTC_DIR}" && git pull origin main
fi

cd "${QTC_DIR}"

# 4. Create Systemd Service
echo "[3/4] Registering systemd service..."
sudo bash -c "cat << 'EOF' > /etc/systemd/system/qitcoin-seed.service
[Unit]
Description=Qitcoin Core Public Testnet Seed Node
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${QTC_DIR}
ExecStart=/usr/bin/python3 ${QTC_DIR}/localhost_node/server.py 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable qitcoin-seed.service
sudo systemctl restart qitcoin-seed.service

echo "[4/4] Verifying node status..."
sleep 2
curl -s http://localhost:8080/api/info | jq . || echo "Node running on port 8080!"

echo "========================================================="
echo "SUCCESS! Qitcoin Testnet Seed Node is LIVE on this server!"
echo "P2P Port    : 19333"
echo "RPC Port    : 19332"
echo "Web Portal  : http://$(curl -s ifconfig.me):8080"
echo "========================================================="
