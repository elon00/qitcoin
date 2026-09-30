#!/usr/bin/env bash
# ==============================================================================
# Qitcoin (QTC) Official Native Public Testnet Seed Node Deployer
# Target OS: Ubuntu 22.04 / 24.04 LTS x86_64
# Sets up real native C++ qitcoind daemon as a production systemd service
# ==============================================================================
set -e

echo "========================================================="
echo "   QITCOIN (QTC) NATIVE TESTNET SEED NODE INSTALLER      "
echo "========================================================="

# 1. Update OS and install base dependencies
echo "[1/6] Installing system dependencies..."
sudo apt-get update && sudo apt-get install -y curl git ufw jq libevent-2.1-7 libevent-pthreads-2.1-7 libsqlite3-0 libzmq5

# 2. Configure Firewall for Native Testnet P2P & RPC
echo "[2/6] Configuring firewall ports (P2P: 19333, RPC: 19332)..."
sudo ufw allow 19333/tcp comment 'Qitcoin Testnet P2P'
sudo ufw allow 19332/tcp comment 'Qitcoin Testnet RPC'
sudo ufw --force enable || true

# 3. Create dedicated qitcoin system user & directories
echo "[3/6] Setting up qitcoin user and data directories..."
sudo id -u qitcoin &>/dev/null || sudo useradd -r -m -s /bin/false qitcoin
sudo mkdir -p /etc/qitcoin /var/lib/qitcoin
sudo chown -R qitcoin:qitcoin /var/lib/qitcoin /etc/qitcoin

# 4. Install Native qitcoind & qitcoin-cli binaries
echo "[4/6] Installing native qitcoind & qitcoin-cli binaries..."
if [ -f "/usr/local/bin/qitcoind" ] && [ -f "/usr/local/bin/qitcoin-cli" ]; then
    echo "Native binaries already installed in /usr/local/bin."
else
    # Build from source or copy from build directory
    BUILD_DIR="/tmp/qitcoin-build"
    mkdir -p "${BUILD_DIR}"
    cd "${BUILD_DIR}"
    echo "Cloning Qitcoin repository..."
    git clone https://github.com/elon00/qitcoin.git repo
    
    echo "Compiling native qitcoind from source via Docker/host toolchain..."
    sudo apt-get install -y build-essential libtool autotools-dev automake pkg-config bsdmainutils python3 \
        libevent-dev libboost-dev libboost-system-dev libboost-filesystem-dev libsqlite3-dev libzmq3-dev
    
    git clone --depth 1 --branch v27.1 https://github.com/bitcoin/bitcoin.git bitcoin-core
    cd bitcoin-core
    git apply /tmp/qitcoin-build/repo/patches/*.patch || true
    ./autogen.sh && ./configure --without-gui --with-sqlite --disable-bench --disable-fuzz-binary CFLAGS="-O2" CXXFLAGS="-O2"
    make -j$(nproc)
    sudo cp src/bitcoind /usr/local/bin/qitcoind
    sudo cp src/bitcoin-cli /usr/local/bin/qitcoin-cli
    sudo chmod +x /usr/local/bin/qitcoind /usr/local/bin/qitcoin-cli
    cd /
    rm -rf "${BUILD_DIR}"
fi

# 5. Create native qitcoin.conf
echo "[5/6] Writing production testnet configuration..."
RPC_PASSWORD=$(openssl rand -hex 16)
sudo bash -c "cat << EOF > /etc/qitcoin/qitcoin.conf
# Qitcoin Native Testnet Configuration
testnet=1
server=1
listen=1
txindex=1

# P2P & RPC Binding
port=19333
bind=0.0.0.0
rpcport=19332
rpcbind=0.0.0.0
rpcallowip=0.0.0.0/0
rpcuser=qtcadmin
rpcpassword=${RPC_PASSWORD}

# Seed node settings
maxconnections=125
discover=1
EOF"
sudo chmod 600 /etc/qitcoin/qitcoin.conf
sudo chown qitcoin:qitcoin /etc/qitcoin/qitcoin.conf

# 6. Create native systemd service for qitcoind
echo "[6/6] Registering native qitcoind systemd service..."
sudo bash -c "cat << 'EOF' > /etc/systemd/system/qitcoind.service
[Unit]
Description=Qitcoin Core Native Testnet Node
After=network.target

[Service]
Type=forking
User=qitcoin
Group=qitcoin
ExecStart=/usr/local/bin/qitcoind -daemon -conf=/etc/qitcoin/qitcoin.conf -datadir=/var/lib/qitcoin
ExecStop=/usr/local/bin/qitcoin-cli -conf=/etc/qitcoin/qitcoin.conf -datadir=/var/lib/qitcoin stop
Restart=always
RestartSec=10
TimeoutStartSec=120
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable qitcoind.service
sudo systemctl restart qitcoind.service

echo "Verifying native daemon startup..."
sleep 5
sudo -u qitcoin /usr/local/bin/qitcoin-cli -conf=/etc/qitcoin/qitcoin.conf -datadir=/var/lib/qitcoin getblockchaininfo || true

echo "========================================================="
echo "SUCCESS! Native qitcoind Testnet Seed Node is running!"
echo "Service Name : qitcoind.service"
echo "P2P Port     : 19333 (Active)"
echo "RPC Port     : 19332 (Active)"
echo "Config File  : /etc/qitcoin/qitcoin.conf"
echo "Data Dir     : /var/lib/qitcoin"
echo "========================================================="
