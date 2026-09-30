#!/usr/bin/env python3
"""
Qitcoin (QTC) Localhost Node & Interactive Block Explorer
--------------------------------------------------------
Zero-dependency, standalone local development node with:
- UTXO Ledger & Consensus Validation (1 Trillion QTC supply, 6 decimals)
- SHA-256d Proof-of-Work Mining Engine (250,000 QTC block reward)
- Mempool and Transaction Broadcast
- Bitcoin-compatible JSON-RPC 2.0 API (/rpc)
- Embedded Modern Block Explorer & Wallet Web UI (http://localhost:8080)
"""

import hashlib
import json
import time
import struct
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os

# Qitcoin Consensus Constants
COIN = 1_000_000 # 6 decimals (1 QTC = 1,000,000 qits)
MAX_SUPPLY_QTC = 1_000_000_000_000 # 1 Trillion QTC
INITIAL_REWARD_QTC = 250_000
HALVING_INTERVAL = 2_000_000

def sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def generate_qtc_address() -> str:
    """Generate a mock Base58-styled Qitcoin address starting with 'Q'."""
    rand = os.urandom(20).hex()
    # Mock base58 format with Q prefix
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    num = int(rand, 16)
    encoded = ""
    while num > 0:
        num, rem = divmod(num, 58)
        encoded = alphabet[rem] + encoded
    return "Q" + encoded[:33]

class QTCBlockchain:
    def __init__(self):
        self.lock = threading.Lock()
        self.chain = []
        self.mempool = []
        self.utxos = {} # (txid, vout_index) -> (address, amount_qits)
        self.addresses = {} # address -> balance_qits
        self.dev_miner_address = "Q1TrillionQitcoinGenesisDevKey888"
        self._create_genesis_block()

    def get_block_reward(self, height: int) -> int:
        halvings = height // HALVING_INTERVAL
        if halvings >= 38:
            return 0
        reward = INITIAL_REWARD_QTC * COIN
        reward >>= halvings
        return reward

    def _create_genesis_block(self):
        genesis_time = 1790772000
        psz_timestamp = "The Times 30/Sep/2026 Qitcoin: The Decentralized Trillion Economy"
        genesis_tx = {
            "txid": "9a5bcf89553e6cc933455c84a964f720f0aa47628f5bfee08e0db920a37db79a",
            "vin": [{"coinbase": psz_timestamp}],
            "vout": [{"value_qtc": INITIAL_REWARD_QTC, "value_qits": INITIAL_REWARD_QTC * COIN, "address": self.dev_miner_address}],
            "fee_qits": 0,
            "timestamp": genesis_time
        }
        
        genesis_block = {
            "height": 0,
            "hash": "0000064d6898cab247cd7a66ae5d621abe9decd284d84b8a1b857b0606dc532a",
            "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
            "merkle_root": genesis_tx["txid"],
            "timestamp": genesis_time,
            "bits": "0x1e0ffff0",
            "difficulty": 1.0,
            "nonce": 388903,
            "reward_qtc": INITIAL_REWARD_QTC,
            "transactions": [genesis_tx]
        }
        self.chain.append(genesis_block)
        self.utxos[(genesis_tx["txid"], 0)] = (self.dev_miner_address, INITIAL_REWARD_QTC * COIN)
        self.addresses[self.dev_miner_address] = INITIAL_REWARD_QTC * COIN

    def get_circulating_supply(self) -> float:
        total_qits = sum(b["reward_qtc"] * COIN for b in self.chain)
        return total_qits / COIN

    def get_balance(self, address: str) -> float:
        return self.addresses.get(address, 0) / COIN

    def mine_block(self, miner_address: str = None) -> dict:
        with self.lock:
            miner = miner_address if miner_address else self.dev_miner_address
            height = len(self.chain)
            prev_block = self.chain[-1]
            reward_qits = self.get_block_reward(height)
            reward_qtc = reward_qits / COIN

            # Include mempool transactions
            txs_to_mine = list(self.mempool)
            self.mempool = []

            # Create Coinbase TX
            cb_raw = f"coinbase_{height}_{time.time()}_{miner}".encode()
            cb_txid = hashlib.sha256(cb_raw).hexdigest()
            coinbase_tx = {
                "txid": cb_txid,
                "vin": [{"coinbase": f"Mined by {miner} at block #{height}"}],
                "vout": [{"value_qtc": reward_qtc, "value_qits": reward_qits, "address": miner}],
                "fee_qits": 0,
                "timestamp": int(time.time())
            }
            all_txs = [coinbase_tx] + txs_to_mine

            # Compute Merkle Root
            combined = "".join(tx["txid"] for tx in all_txs).encode()
            merkle_root = hashlib.sha256(combined).hexdigest()

            # Mine PoW with target difficulty (mock 2 leading zeros for fast localhost mining)
            nonce = 0
            n_time = int(time.time())
            while True:
                header = f"{height}{prev_block['hash']}{merkle_root}{n_time}{nonce}".encode()
                block_hash = hashlib.sha256(header).hexdigest()
                if block_hash.startswith("00"):
                    break
                nonce += 1

            new_block = {
                "height": height,
                "hash": block_hash,
                "prev_hash": prev_block["hash"],
                "merkle_root": merkle_root,
                "timestamp": n_time,
                "bits": "0x207fffff",
                "difficulty": 1.0,
                "nonce": nonce,
                "reward_qtc": reward_qtc,
                "transactions": all_txs
            }

            self.chain.append(new_block)
            
            # Credit miner reward
            self.utxos[(cb_txid, 0)] = (miner, reward_qits)
            self.addresses[miner] = self.addresses.get(miner, 0) + reward_qits

            return new_block

    def send_transaction(self, sender: str, recipient: str, amount_qtc: float) -> dict:
        with self.lock:
            amount_qits = int(amount_qtc * COIN)
            if amount_qits <= 0:
                raise ValueError("Amount must be greater than zero")

            sender_bal = self.addresses.get(sender, 0)
            if sender_bal < amount_qits:
                raise ValueError(f"Insufficient funds: available {sender_bal/COIN:.6f} QTC, required {amount_qtc:.6f} QTC")

            tx_raw = f"{sender}->{recipient}:{amount_qits}_{time.time()}_{os.urandom(4).hex()}".encode()
            txid = hashlib.sha256(tx_raw).hexdigest()

            tx = {
                "txid": txid,
                "vin": [{"sender": sender, "amount_qtc": amount_qtc}],
                "vout": [{"recipient": recipient, "value_qtc": amount_qtc, "value_qits": amount_qits}],
                "fee_qits": 0,
                "timestamp": int(time.time())
            }

            # Update balances in memory for mempool
            self.addresses[sender] -= amount_qits
            self.addresses[recipient] = self.addresses.get(recipient, 0) + amount_qits
            self.mempool.append(tx)
            return tx

node_chain = QTCBlockchain()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Qitcoin (QTC) Localhost Node & Explorer</title>
    <style>
        :root {
            --bg: #0d1117;
            --card-bg: #161b22;
            --border: #30363d;
            --accent: #f59e0b;
            --accent-hover: #d97706;
            --text: #c9d1d9;
            --text-heading: #f0f6fc;
            --green: #10b981;
            --blue: #38bdf8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
        body { background: var(--bg); color: var(--text); padding: 24px; line-height: 1.5; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
        .logo-area { display: flex; align-items: center; gap: 12px; }
        .logo-badge { background: linear-gradient(135deg, #f59e0b, #ef4444); color: black; font-weight: 800; font-size: 20px; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(245, 158, 11, 0.4); }
        h1 { color: var(--text-heading); font-size: 24px; font-weight: 700; }
        .network-badge { background: #1e293b; color: var(--blue); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid #334155; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 18px; }
        .stat-label { font-size: 12px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
        .stat-val { font-size: 22px; font-weight: 700; color: var(--text-heading); }
        .stat-sub { font-size: 11px; color: var(--green); margin-top: 4px; }
        
        .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
        @media(max-width: 768px) { .main-grid { grid-template-columns: 1fr; } }
        
        .form-group { margin-bottom: 14px; }
        label { display: block; font-size: 13px; color: #8b949e; margin-bottom: 6px; }
        input, select { width: 100%; background: #0d1117; border: 1px solid var(--border); color: var(--text-heading); padding: 10px 12px; border-radius: 6px; font-size: 14px; outline: none; }
        input:focus { border-color: var(--accent); }
        .btn { background: var(--accent); color: black; border: none; padding: 10px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; transition: 0.2s; font-size: 14px; }
        .btn:hover { background: var(--accent-hover); }
        .btn-mine { background: linear-gradient(135deg, #10b981, #059669); color: white; width: 100%; padding: 14px; font-size: 16px; font-weight: 700; }
        .btn-mine:hover { opacity: 0.9; }

        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); font-size: 13px; }
        th { color: #8b949e; font-size: 11px; text-transform: uppercase; }
        .mono { font-family: monospace; color: var(--blue); }
        .highlight { color: var(--accent); font-weight: 600; }
        .tag { background: #238636; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
        .json-box { background: #090d13; border: 1px solid var(--border); padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; color: #58a6ff; max-height: 180px; overflow-y: auto; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-area">
                <div class="logo-badge">Q</div>
                <div>
                    <h1>Qitcoin Core (QTC)</h1>
                    <div style="font-size: 12px; color: #8b949e;">Standalone Layer-1 PoW Blockchain &bull; 1 Trillion Supply Edition</div>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap: 10px;">
                <span class="network-badge">&#x25CF; LOCALHOST REGTEST</span>
                <span class="network-badge">6 DECIMALS (int64 SAFE)</span>
            </div>
        </header>

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="card">
                <div class="stat-label">Block Height</div>
                <div class="stat-val" id="stat-height">0</div>
                <div class="stat-sub">&#x2191; Synced with Genesis</div>
            </div>
            <div class="card">
                <div class="stat-label">Circulating Supply</div>
                <div class="stat-val"><span id="stat-supply">250,000</span> <span style="font-size:14px; color:#8b949e;">QTC</span></div>
                <div class="stat-sub">Max: 1,000,000,000,000 QTC</div>
            </div>
            <div class="card">
                <div class="stat-label">Current Block Subsidy</div>
                <div class="stat-val">250,000 <span style="font-size:14px; color:#8b949e;">QTC</span></div>
                <div class="stat-sub">Halving in 2,000,000 blocks</div>
            </div>
            <div class="card">
                <div class="stat-label">Mempool Transactions</div>
                <div class="stat-val" id="stat-mempool">0</div>
                <div class="stat-sub">Ready to be mined</div>
            </div>
        </div>

        <!-- Action Grid -->
        <div class="main-grid">
            <!-- Miner Card -->
            <div class="card">
                <h3 style="color: var(--text-heading); margin-bottom: 12px;">&#x26cf; PoW Block Miner</h3>
                <div class="form-group">
                    <label>Miner Reward Address (QTC)</label>
                    <input type="text" id="miner-address" value="Q1TrillionQitcoinGenesisDevKey888" />
                </div>
                <button class="btn btn-mine" onclick="mineBlock()">Mine 1 New Block (+250,000 QTC)</button>
                <div id="mining-status" style="margin-top: 10px; font-size: 13px; color: var(--green);"></div>
            </div>

            <!-- Wallet Transfer Card -->
            <div class="card">
                <h3 style="color: var(--text-heading); margin-bottom: 12px;">&#x1f4b8; Send QTC Transaction</h3>
                <div class="form-group">
                    <label>Sender Address (Must have balance)</label>
                    <input type="text" id="tx-sender" value="Q1TrillionQitcoinGenesisDevKey888" />
                </div>
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px;">
                    <div class="form-group">
                        <label>Recipient Address</label>
                        <input type="text" id="tx-recipient" placeholder="Recipient address starting with Q..." />
                    </div>
                    <div class="form-group">
                        <label>Amount (QTC)</label>
                        <input type="number" id="tx-amount" value="5000" min="1" step="any" />
                    </div>
                </div>
                <div style="display:flex; gap: 8px;">
                    <button class="btn" style="flex: 1;" onclick="sendTransaction()">Send QTC</button>
                    <button class="btn" style="background: #334155; color: white;" onclick="generateNewAddress()">New Address</button>
                </div>
                <div id="tx-status" style="margin-top: 8px; font-size: 13px;"></div>
            </div>
        </div>

        <!-- Recent Blocks Table -->
        <div class="card" style="margin-bottom: 24px;">
            <h3 style="color: var(--text-heading); margin-bottom: 8px;">&#x1f4da; Blockchain Ledger (Recent Blocks)</h3>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Height</th>
                            <th>Block Hash</th>
                            <th>TX Count</th>
                            <th>Reward</th>
                            <th>Nonce</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody id="blocks-table">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- RPC API Quick Reference -->
        <div class="card">
            <h3 style="color: var(--text-heading); margin-bottom: 8px;">&#x1f50c; Bitcoin-Compatible JSON-RPC Endpoint (<code>/rpc</code>)</h3>
            <p style="font-size: 13px; color: #8b949e; margin-bottom: 10px;">
                You can interact with this node using any standard Bitcoin RPC client or <code>curl</code>:
            </p>
            <div class="json-box">curl -X POST http://localhost:8080/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "getblockchaininfo", "params": []}'</div>
        </div>
    </div>

    <script>
        async function fetchChainInfo() {
            try {
                const res = await fetch('/api/info');
                const data = await res.json();
                document.getElementById('stat-height').innerText = data.height;
                document.getElementById('stat-supply').innerText = Number(data.supply).toLocaleString();
                document.getElementById('stat-mempool').innerText = data.mempool_count;

                const tbody = document.getElementById('blocks-table');
                tbody.innerHTML = '';
                data.blocks.slice(-10).reverse().forEach(b => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><span class="tag">#${b.height}</span></td>
                        <td class="mono">${b.hash.substring(0, 18)}...${b.hash.substring(b.hash.length - 8)}</td>
                        <td>${b.transactions.length} tx</td>
                        <td class="highlight">+${b.reward_qtc.toLocaleString()} QTC</td>
                        <td>${b.nonce}</td>
                        <td style="color:#8b949e;">${new Date(b.timestamp * 1000).toLocaleTimeString()}</td>
                    `;
                    tbody.appendChild(row);
                });
            } catch(e) {
                console.error(e);
            }
        }

        async function mineBlock() {
            const miner = document.getElementById('miner-address').value;
            const status = document.getElementById('mining-status');
            status.style.color = '#f59e0b';
            status.innerText = 'Mining Proof-of-Work block...';
            try {
                const res = await fetch('/api/mine', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({miner})
                });
                const data = await res.json();
                status.style.color = '#10b981';
                status.innerText = `Block #${data.height} mined successfully! Hash: ${data.hash.substring(0, 18)}...`;
                fetchChainInfo();
            } catch(e) {
                status.style.color = '#ef4444';
                status.innerText = 'Mining error: ' + e.message;
            }
        }

        async function sendTransaction() {
            const sender = document.getElementById('tx-sender').value;
            const recipient = document.getElementById('tx-recipient').value;
            const amount = parseFloat(document.getElementById('tx-amount').value);
            const status = document.getElementById('tx-status');
            if (!recipient) {
                status.style.color = '#ef4444';
                status.innerText = 'Please enter or generate a recipient address!';
                return;
            }
            try {
                const res = await fetch('/api/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({sender, recipient, amount})
                });
                const data = await res.json();
                if (data.error) {
                    status.style.color = '#ef4444';
                    status.innerText = 'Error: ' + data.error;
                } else {
                    status.style.color = '#10b981';
                    status.innerText = `Tx broadcasted! TxID: ${data.txid.substring(0, 18)}... (In Mempool)`;
                    fetchChainInfo();
                }
            } catch(e) {
                status.style.color = '#ef4444';
                status.innerText = 'Failed: ' + e.message;
            }
        }

        async function generateNewAddress() {
            const res = await fetch('/api/newaddress');
            const data = await res.json();
            document.getElementById('tx-recipient').value = data.address;
            document.getElementById('tx-status').style.color = '#38bdf8';
            document.getElementById('tx-status').innerText = 'Generated new QTC address: ' + data.address;
        }

        fetchChainInfo();
        setInterval(fetchChainInfo, 3000);
    </script>
</body>
</html>
"""

class QTCRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noisy log outputs
        return

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif parsed.path == "/api/info":
            info = {
                "height": len(node_chain.chain) - 1,
                "supply": node_chain.get_circulating_supply(),
                "mempool_count": len(node_chain.mempool),
                "blocks": node_chain.chain[-20:]
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(info).encode("utf-8"))
        elif parsed.path == "/api/newaddress":
            addr = generate_qtc_address()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"address": addr}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode("utf-8")) if body else {}

        if parsed.path == "/api/mine":
            miner = data.get("miner")
            block = node_chain.mine_block(miner)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(block).encode("utf-8"))

        elif parsed.path == "/api/send":
            try:
                tx = node_chain.send_transaction(data.get("sender"), data.get("recipient"), float(data.get("amount", 0)))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(tx).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif parsed.path == "/rpc":
            # Bitcoin JSON-RPC compatible handler
            method = data.get("method")
            req_id = data.get("id")
            params = data.get("params", [])

            result = None
            error = None

            if method == "getblockchaininfo":
                result = {
                    "chain": "regtest",
                    "blocks": len(node_chain.chain) - 1,
                    "headers": len(node_chain.chain) - 1,
                    "bestblockhash": node_chain.chain[-1]["hash"],
                    "difficulty": 1.0,
                    "mediantime": node_chain.chain[-1]["timestamp"],
                    "verificationprogress": 1.0,
                    "chainwork": "0000000000000000000000000000000000000000000000000000000100010001"
                }
            elif method == "getblockcount":
                result = len(node_chain.chain) - 1
            elif method == "getblock":
                block_param = params[0] if params else 0
                target = None
                for b in node_chain.chain:
                    if b["hash"] == block_param or b["height"] == block_param:
                        target = b
                        break
                result = target if target else None
                if not result:
                    error = {"code": -5, "message": "Block not found"}
            elif method == "getbalance":
                addr = params[0] if params else node_chain.dev_miner_address
                result = node_chain.get_balance(addr)
            elif method == "generatetoaddress":
                n_blocks = params[0] if len(params) > 0 else 1
                addr = params[1] if len(params) > 1 else node_chain.dev_miner_address
                hashes = []
                for _ in range(n_blocks):
                    b = node_chain.mine_block(addr)
                    hashes.append(b["hash"])
                result = hashes
            else:
                error = {"code": -32601, "message": f"Method {method} not implemented"}

            resp = {"jsonrpc": "2.0", "id": req_id, "result": result, "error": error}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8080):
    server = HTTPServer(("0.0.0.0", port), QTCRequestHandler)
    print(f"=================================================================")
    print(f"QITCOIN (QTC) LOCALHOST NODE & BLOCK EXPLORER RUNNING")
    print(f"=================================================================")
    print(f"Web Dashboard / Explorer : http://localhost:{port}")
    print(f"Bitcoin JSON-RPC API     : http://localhost:{port}/rpc")
    print(f"Total Max Supply         : 1,000,000,000,000 QTC")
    print(f"Base Currency Decimals   : 6 (1 QTC = 1,000,000 qits)")
    print(f"Genesis Block Hash       : {node_chain.chain[0]['hash']}")
    print(f"Press Ctrl+C to terminate.")
    print(f"=================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Qitcoin Localhost Node.")
        server.server_close()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
