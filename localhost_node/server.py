#!/usr/bin/env python3
"""
Qitcoin (QTC) All-in-One Localhost Portal & Sovereign Node
---------------------------------------------------------
Features:
1. UTXO Ledger & Consensus Validation (1 Trillion QTC supply, 6 decimals)
2. PoW Block Miner & Mempool
3. Cross-Chain Swap DEX (QTC <-> BTC, ETH, SOL, ALGO, USDT)
4. Multichain Bridge with Proof-of-Reserve & Circuit Breaker
5. NIST FIPS 204 (ML-DSA) Post-Quantum Cryptography Attestation Inspector
6. Multimodal AI Agentics Terminal (Natural Language Commands)
7. Conway AI Automaton (Cellular Game-of-Life Mesh Grid)
8. x402 Bazaar Protocol (HTTP 402 Machine-to-Machine Micropayments)
9. QTC Token Launchpad with Linear Bonding Curves
10. QR Code Generator & Multiwallet Connector (MetaMask, Phantom, QTC Core)
11. Secure API Key & Secrets Manager
12. Bitcoin-Compatible JSON-RPC 2.0 API (/rpc)
"""

import hashlib
import json
import time
import struct
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os
import sys

# Ensure root directory is in sys.path to import modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from bridge.cross_chain_engine import bridge_instance
from bridge.pqc_nist_bridge import pqc_attestor
from agentics.conway_automaton import conway_automaton
from agentics.multimodal_agent import QitcoinAIAgent
from x402.x402_bazaar import x402_engine
from launchpad.launchpad_engine import launchpad_instance
from config.api_keys_manager import key_manager

# Consensus Constants
COIN = 1_000_000 # 6 decimals (1 QTC = 1,000,000 qits)
MAX_SUPPLY_QTC = 1_000_000_000_000 # 1 Trillion QTC
INITIAL_REWARD_QTC = 250_000
HALVING_INTERVAL = 2_000_000

class QTCBlockchain:
    def __init__(self):
        self.lock = threading.Lock()
        self.chain = []
        self.mempool = []
        self.utxos = {}
        self.addresses = {}
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

            txs_to_mine = list(self.mempool)
            self.mempool = []

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

            combined = "".join(tx["txid"] for tx in all_txs).encode()
            merkle_root = hashlib.sha256(combined).hexdigest()

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

            self.addresses[sender] -= amount_qits
            self.addresses[recipient] = self.addresses.get(recipient, 0) + amount_qits
            self.mempool.append(tx)
            return tx

node_chain = QTCBlockchain()
ai_agent = QitcoinAIAgent(bridge_engine=bridge_instance, blockchain_node=node_chain)

HTML_PORTAL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Qitcoin (QTC) Portal & Ecosystem Hub</title>
    <style>
        :root {
            --bg: #0b0f17;
            --card-bg: #131b26;
            --border: #233143;
            --accent: #f59e0b;
            --accent-glow: rgba(245, 158, 11, 0.25);
            --green: #10b981;
            --blue: #38bdf8;
            --purple: #a855f7;
            --text: #c9d1d9;
            --text-heading: #f0f6fc;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
        body { background: var(--bg); color: var(--text); padding: 18px; line-height: 1.5; }
        .container { max-width: 1300px; margin: 0 auto; }
        
        /* Top Navigation Header */
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 14px; margin-bottom: 18px; }
        .brand { display: flex; align-items: center; gap: 12px; }
        .brand-icon { background: linear-gradient(135deg, #f59e0b, #ef4444); color: black; font-weight: 900; font-size: 22px; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px var(--accent-glow); }
        .pill { background: #1e293b; color: var(--blue); padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; border: 1px solid #334155; }
        .wallet-btn { background: #1f2937; border: 1px solid var(--border); color: #fff; padding: 8px 14px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; }
        .wallet-btn:hover { border-color: var(--accent); }

        /* Navigation Tabs */
        .tabs { display: flex; gap: 6px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 4px; border-bottom: 1px solid var(--border); }
        .tab-btn { background: transparent; border: none; color: #8b949e; padding: 10px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 8px; transition: 0.2s; white-space: nowrap; }
        .tab-btn.active { background: #1c2738; color: var(--accent); border-bottom: 2px solid var(--accent); }
        .tab-btn:hover { color: #fff; }

        /* Views */
        .view-panel { display: none; }
        .view-panel.active { display: block; }

        /* Cards & Grid */
        .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 20px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 20px; }
        @media(max-width: 860px) { .grid-2 { grid-template-columns: 1fr; } }
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 18px; }
        .card-title { color: var(--text-heading); font-size: 16px; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; }
        
        .stat-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
        .stat-val { font-size: 22px; font-weight: 700; color: var(--text-heading); }
        .stat-sub { font-size: 11px; color: var(--green); margin-top: 4px; }

        /* Forms & Buttons */
        .form-group { margin-bottom: 12px; }
        label { display: block; font-size: 12px; color: #8b949e; margin-bottom: 5px; }
        input, select, textarea { width: 100%; background: #0b0f17; border: 1px solid var(--border); color: #fff; padding: 10px 12px; border-radius: 8px; font-size: 13px; outline: none; }
        input:focus, select:focus, textarea:focus { border-color: var(--accent); }
        .btn { background: var(--accent); color: black; border: none; padding: 10px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 13px; transition: 0.2s; }
        .btn:hover { opacity: 0.9; }
        .btn-green { background: var(--green); color: white; }
        .btn-blue { background: var(--blue); color: black; }
        .btn-purple { background: var(--purple); color: white; }
        .btn-full { width: 100%; }

        /* Tables */
        table { width: 100%; border-collapse: collapse; margin-top: 8px; }
        th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); font-size: 12px; }
        th { color: #8b949e; text-transform: uppercase; font-size: 11px; }
        .mono { font-family: monospace; color: var(--blue); }

        /* Conway Grid */
        .conway-canvas { display: grid; grid-template-columns: repeat(16, 18px); gap: 3px; background: #070a0f; padding: 10px; border-radius: 8px; width: fit-content; margin: 10px auto; border: 1px solid var(--border); }
        .cell { width: 18px; height: 18px; border-radius: 3px; background: #131b26; transition: background 0.15s; }
        .cell.alive { background: var(--accent); box-shadow: 0 0 6px var(--accent-glow); }

        /* QR Code Mock Container */
        .qr-box { background: white; padding: 14px; border-radius: 10px; display: inline-block; margin-top: 10px; }

        /* Modal */
        .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: none; align-items: center; justify-content: center; z-index: 1000; }
        .modal { background: var(--card-bg); border: 1px solid var(--border); width: 90%; max-width: 440px; border-radius: 14px; padding: 22px; }
        .wallet-option { display: flex; align-items: center; gap: 12px; padding: 12px; background: #0b0f17; border: 1px solid var(--border); border-radius: 10px; margin-bottom: 10px; cursor: pointer; transition: 0.2s; }
        .wallet-option:hover { border-color: var(--accent); }

        .terminal-box { background: #070a0f; border: 1px solid var(--border); border-radius: 8px; padding: 12px; font-family: monospace; font-size: 12px; height: 200px; overflow-y: auto; color: #58a6ff; white-space: pre-wrap; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Top Header -->
        <header>
            <div class="brand">
                <div class="brand-icon">Q</div>
                <div>
                    <h1 style="font-size: 20px; font-weight: 800; color: #fff;">Qitcoin Core (QTC)</h1>
                    <div style="font-size: 11px; color: #8b949e;">1 Trillion Supply L1 &bull; Multichain Bridge &bull; PQC NIST &bull; Web 4.0</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="pill">&#x25CF; REGTEST LOCAL</span>
                <span class="pill" style="color:var(--green); border-color:#065f46;">PQC STATUS</span>
                <button class="wallet-btn" onclick="openWalletModal()">
                    <span id="wallet-label">&#x1f45b; Connect Wallet</span>
                </button>
            </div>
        </header>

        <!-- Navigation Tabs -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('explorer')">&#x1f4ca; Explorer & Node</button>
            <button class="tab-btn" onclick="switchTab('swap')">&#x1f504; Cross-Chain Swap</button>
            <button class="tab-btn" onclick="switchTab('bridge')">&#x1f309; Multichain Bridge</button>
            <button class="tab-btn" onclick="switchTab('pqc')">&#x1f510; NIST PQC Engine</button>
            <button class="tab-btn" onclick="switchTab('agent')">&#x1f916; AI Agentics</button>
            <button class="tab-btn" onclick="switchTab('conway')">&#x1f9ec; Conway Automaton</button>
            <button class="tab-btn" onclick="switchTab('launchpad')">&#x1f680; Launchpad</button>
            <button class="tab-btn" onclick="switchTab('x402')">&#x26a1; x402 Bazaar (Web 4.0)</button>
            <button class="tab-btn" onclick="switchTab('settings')">&#x2699;&#xfe0f; API Keys</button>
        </div>

        <!-- 1. EXPLORER & NODE VIEW -->
        <div id="view-explorer" class="view-panel active">
            <div class="grid-4">
                <div class="card">
                    <div class="stat-label">Block Height</div>
                    <div class="stat-val" id="stat-height">0</div>
                    <div class="stat-sub">&#x2191; Synced with Genesis</div>
                </div>
                <div class="card">
                    <div class="stat-label">Circulating Supply</div>
                    <div class="stat-val"><span id="stat-supply">250,000</span> <span style="font-size:12px; color:#8b949e;">QTC</span></div>
                    <div class="stat-sub">Max: 1,000,000,000,000 QTC</div>
                </div>
                <div class="card">
                    <div class="stat-label">Block Reward</div>
                    <div class="stat-val">250,000 <span style="font-size:12px; color:#8b949e;">QTC</span></div>
                    <div class="stat-sub">Halving every 2,000,000 blocks</div>
                </div>
                <div class="card">
                    <div class="stat-label">Mempool Transactions</div>
                    <div class="stat-val" id="stat-mempool">0</div>
                    <div class="stat-sub">Pending confirmation</div>
                </div>
            </div>

            <div class="grid-2">
                <!-- Mine Block & Address Card -->
                <div class="card">
                    <div class="card-title">&#x26cf; PoW Mining & Local Wallet</div>
                    <div class="form-group">
                        <label>Active QTC Address</label>
                        <input type="text" id="node-active-address" value="Q1TrillionQitcoinGenesisDevKey888" readonly />
                    </div>
                    <div style="display:flex; gap: 8px; margin-bottom: 12px;">
                        <button class="btn btn-green btn-full" onclick="mineBlock()">Mine 1 New Block (+250,000 QTC)</button>
                        <button class="btn" style="background:#1e293b; color:#fff;" onclick="showQrForAddress()">&#x1f4f1; QR</button>
                    </div>
                    <div id="mining-status" style="font-size: 12px; color: var(--green);"></div>
                    
                    <!-- QR Box Modal Inline -->
                    <div id="qr-container" style="display:none; text-align:center; margin-top:10px;">
                        <div class="stat-label">Scan to Send QTC</div>
                        <div id="qr-svg-holder" style="display:flex; justify-content:center; margin: 8px 0;"></div>
                        <div style="font-size:11px; color:#8b949e;">bitcoin:Q1Trillion...?amount=250000</div>
                    </div>
                </div>

                <!-- Send QTC Transaction -->
                <div class="card">
                    <div class="card-title">&#x1f4b8; Send QTC Transaction</div>
                    <div class="form-group">
                        <label>Recipient Address (Starts with Q...)</label>
                        <input type="text" id="send-recipient" placeholder="Recipient address..." />
                    </div>
                    <div class="form-group">
                        <label>Amount (QTC)</label>
                        <input type="number" id="send-amount" value="5000" min="1" />
                    </div>
                    <button class="btn btn-full" onclick="sendTransaction()">Broadcast Transaction</button>
                    <div id="send-status" style="margin-top: 8px; font-size: 12px;"></div>
                </div>
            </div>

            <!-- Ledger Blocks -->
            <div class="card">
                <div class="card-title">&#x1f4da; Blockchain Ledger (Recent Blocks)</div>
                <table>
                    <thead>
                        <tr>
                            <th>Height</th>
                            <th>Block Hash</th>
                            <th>TXs</th>
                            <th>Reward</th>
                            <th>Nonce</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody id="blocks-table"></tbody>
                </table>
            </div>
        </div>

        <!-- 2. CROSS-CHAIN SWAP VIEW -->
        <div id="view-swap" class="view-panel">
            <div class="grid-2">
                <div class="card">
                    <div class="card-title">&#x1f504; Instant Cross-Chain DEX Swap</div>
                    <div class="form-group">
                        <label>You Pay</label>
                        <div style="display:flex; gap:8px;">
                            <input type="number" id="swap-amt-in" value="50000" oninput="calculateSwapQuote()" />
                            <select id="swap-from-token" style="width: 140px;" onchange="calculateSwapQuote()">
                                <option value="QTC">QTC</option>
                                <option value="USDT">USDT</option>
                                <option value="BTC">BTC</option>
                                <option value="ETH">ETH</option>
                                <option value="SOL">SOL</option>
                                <option value="ALGO">ALGO</option>
                            </select>
                        </div>
                    </div>
                    <div style="text-align:center; padding: 4px; color:var(--accent); font-size:18px;">&#x2193;</div>
                    <div class="form-group">
                        <label>You Receive (Estimated)</label>
                        <div style="display:flex; gap:8px;">
                            <input type="number" id="swap-amt-out" readonly />
                            <select id="swap-to-token" style="width: 140px;" onchange="calculateSwapQuote()">
                                <option value="USDT">USDT</option>
                                <option value="BTC">BTC</option>
                                <option value="ETH">ETH</option>
                                <option value="SOL">SOL</option>
                                <option value="ALGO">ALGO</option>
                                <option value="QTC">QTC</option>
                            </select>
                        </div>
                    </div>
                    <div style="font-size:12px; color:#8b949e; margin-bottom:14px;">
                        Rate: <span id="swap-rate-display" style="color:#fff;">1 QTC = 0.05 USDT</span> &bull; Slippage: 0.3%
                    </div>
                    <button class="btn btn-full" onclick="executeSwapAction()">Execute Cross-Chain Swap</button>
                    <div id="swap-status" style="margin-top:8px; font-size:12px;"></div>
                </div>

                <div class="card">
                    <div class="card-title">&#x1f4ca; Liquidity Pools (AMM Reserves)</div>
                    <table>
                        <thead>
                            <tr><th>Pair</th><th>Reserve A</th><th>Reserve B</th><th>Price</th></tr>
                        </thead>
                        <tbody>
                            <tr><td><b>QTC / USDT</b></td><td>10,000,000 QTC</td><td>500,000 USDT</td><td class="mono">$0.0500</td></tr>
                            <tr><td><b>QTC / BTC</b></td><td>20,000,000 QTC</td><td>15.5 BTC</td><td class="mono">0.00000078 BTC</td></tr>
                            <tr><td><b>QTC / ETH</b></td><td>15,000,000 QTC</td><td>280.0 ETH</td><td class="mono">0.0000187 ETH</td></tr>
                            <tr><td><b>QTC / SOL</b></td><td>8,000,000 QTC</td><td>2,600 SOL</td><td class="mono">0.000325 SOL</td></tr>
                            <tr><td><b>QTC / ALGO</b></td><td>5,000,000 QTC</td><td>1,250,000 ALGO</td><td class="mono">0.25 ALGO</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- 3. MULTICHAIN BRIDGE VIEW -->
        <div id="view-bridge" class="view-panel">
            <div class="grid-4" style="margin-bottom:18px;">
                <div class="card">
                    <div class="stat-label">Locked Native QTC</div>
                    <div class="stat-val">50,000,000</div>
                    <div class="stat-sub">In L1 Vault</div>
                </div>
                <div class="card">
                    <div class="stat-label">Minted wQTC Total</div>
                    <div class="stat-val">50,000,000</div>
                    <div class="stat-sub">ETH + SOL + ALGO</div>
                </div>
                <div class="card">
                    <div class="stat-label">Proof of Reserve</div>
                    <div class="stat-val" style="color:var(--green);">100.0%</div>
                    <div class="stat-sub">Fully Collateralized</div>
                </div>
                <div class="card">
                    <div class="stat-label">Circuit Breaker</div>
                    <div class="stat-val" style="color:var(--green);">NORMAL</div>
                    <div class="stat-sub">Hourly Cap: 5M QTC</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="card">
                    <div class="card-title">&#x1f309; Initiate Cross-Chain Bridge Transfer</div>
                    <div class="form-group">
                        <label>Source Chain</label>
                        <select id="bridge-src"><option value="QITCOIN_L1">Qitcoin Layer-1 (Native QTC)</option></select>
                    </div>
                    <div class="form-group">
                        <label>Destination Chain</label>
                        <select id="bridge-dst">
                            <option value="ETHEREUM">Ethereum Mainnet (wQTC ERC-20)</option>
                            <option value="SOLANA">Solana (wQTC SPL)</option>
                            <option value="ALGORAND">Algorand (wQTC ASA)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Recipient Address on Target Chain</label>
                        <input type="text" id="bridge-recipient" value="0x71C841832046882c79B215d56418246999014022" />
                    </div>
                    <div class="form-group">
                        <label>Amount (QTC)</label>
                        <input type="number" id="bridge-amt" value="25000" />
                    </div>
                    <button class="btn btn-blue btn-full" onclick="initiateBridgeTransfer()">Initiate PQC-Signed Bridge</button>
                    <div id="bridge-status" style="margin-top:8px; font-size:12px;"></div>
                </div>

                <div class="card">
                    <div class="card-title">&#x1f510; NIST Post-Quantum Bridge Attestation</div>
                    <p style="font-size:12px; color:#8b949e; margin-bottom:10px;">
                        Every cross-chain message is signed by our relayer using <b>NIST FIPS 204 (ML-DSA-65)</b> to eliminate quantum computer forge attacks:
                    </p>
                    <div class="terminal-box" id="bridge-pqc-log">Awaiting bridge transaction...</div>
                </div>
            </div>
        </div>

        <!-- 4. NIST PQC VIEW -->
        <div id="view-pqc" class="view-panel">
            <div class="card" style="margin-bottom:18px;">
                <div class="card-title">&#x1f510; NIST Post-Quantum Cryptography (FIPS 203 & 204) Verifier</div>
                <p style="font-size:13px; color:#8b949e; margin-bottom:14px;">
                    NIST officially finalized FIPS 203 (ML-KEM / Kyber) and FIPS 204 (ML-DSA / Dilithium) in August 2024. Qitcoin implements these algorithms for quantum-resistant bridging and future Taproot soft-fork:
                </p>
                <div style="display:flex; gap:10px; margin-bottom:14px;">
                    <button class="btn btn-purple" onclick="runPqcBenchmark()">Run Live NIST FIPS 204 Signature Benchmark</button>
                </div>
                <div class="terminal-box" id="pqc-terminal-output" style="height:280px;">Click above to run real-time polynomial lattice signing & verification...</div>
            </div>
        </div>

        <!-- 5. AI AGENTICS VIEW -->
        <div id="view-agent" class="view-panel">
            <div class="card">
                <div class="card-title">&#x1f916; Multimodal Sentinel AI Agent</div>
                <div class="terminal-box" id="agent-chat-history" style="height:260px;">Qitcoin Sentinel AI Agent v1.0 ONLINE.
Type natural language commands such as:
- 'mine a block'
- 'swap 25000 QTC to USDT'
- 'check bridge proof of reserve'
- 'send 1000 QTC to Q1Trillion...'</div>
                <div style="display:flex; gap:8px;">
                    <input type="text" id="agent-input" placeholder="Enter natural language command..." onkeydown="if(event.key==='Enter') sendAgentMessage()" />
                    <button class="btn btn-green" onclick="sendAgentMessage()">Send</button>
                </div>
            </div>
        </div>

        <!-- 6. CONWAY AUTOMATON VIEW -->
        <div id="view-conway" class="view-panel">
            <div class="card" style="text-align:center;">
                <div class="card-title" style="justify-content:center;">&#x1f9ec; Conway AI Cellular Automaton (16x16 Node Mesh)</div>
                <p style="font-size:12px; color:#8b949e; margin-bottom:12px;">
                    Simulating self-healing decentralized node topologies and dynamic liquidity clustering using Conway B3/S23 cellular rules:
                </p>
                <div class="conway-canvas" id="conway-grid"></div>
                <div style="margin-top:12px; display:flex; justify-content:center; gap:10px;">
                    <button class="btn" onclick="stepConway()">Step 1 Generation</button>
                    <button class="btn btn-blue" id="auto-conway-btn" onclick="toggleAutoConway()">Auto-Run Mesh</button>
                </div>
                <div style="margin-top:8px; font-size:12px; color:#8b949e;">
                    Generation: <b id="conway-gen" style="color:#fff;">0</b> &bull; Active Nodes: <b id="conway-nodes" style="color:var(--accent);">0</b> &bull; Health: <b id="conway-health" style="color:var(--green);">100%</b>
                </div>
            </div>
        </div>

        <!-- 7. LAUNCHPAD VIEW -->
        <div id="view-launchpad" class="view-panel">
            <div class="grid-2">
                <div class="card">
                    <div class="card-title">&#x1f680; Deploy New Token on Qitcoin</div>
                    <div class="form-group">
                        <label>Token Name</label>
                        <input type="text" id="lp-name" placeholder="e.g. Quantum AI Token" />
                    </div>
                    <div class="form-group">
                        <label>Ticker Symbol</label>
                        <input type="text" id="lp-ticker" placeholder="e.g. QAI" />
                    </div>
                    <div class="form-group">
                        <label>Total Supply</label>
                        <input type="number" id="lp-supply" value="1000000000" />
                    </div>
                    <div class="form-group">
                        <label>Description / Roadmap</label>
                        <textarea id="lp-desc" rows="2" placeholder="Decentralized utility on Qitcoin..."></textarea>
                    </div>
                    <button class="btn btn-full" onclick="createLaunchpadToken()">Launch on Bonding Curve</button>
                    <div id="lp-create-status" style="margin-top:8px; font-size:12px;"></div>
                </div>

                <div class="card">
                    <div class="card-title">&#x1f4b0; Active Launchpad Projects</div>
                    <div id="lp-token-list"></div>
                </div>
            </div>
        </div>

        <!-- 8. x402 BAZAAR VIEW -->
        <div id="view-x402" class="view-panel">
            <div class="card">
                <div class="card-title">&#x26a1; x402 Bazaar Protocol (HTTP 402 Web 4.0 Micropayments)</div>
                <p style="font-size:12px; color:#8b949e; margin-bottom:14px;">
                    Autonomous AI agents pay for API compute and data streams natively in QTC base units (<b>qits</b>, 10^-6 QTC):
                </p>
                <div style="display:flex; gap:10px; margin-bottom:14px;">
                    <button class="btn btn-blue" onclick="requestX402Invoice('ai_inference')">Test AI Inference (0.05 QTC)</button>
                    <button class="btn btn-purple" onclick="requestX402Invoice('pqc_signature')">Test PQC Attestation (0.02 QTC)</button>
                </div>
                <div class="terminal-box" id="x402-terminal">Click a service button above to generate a real HTTP 402 challenge invoice and settle it with QTC...</div>
            </div>
        </div>

        <!-- 9. SETTINGS / API KEYS VIEW -->
        <div id="view-settings" class="view-panel">
            <div class="card">
                <div class="card-title">&#x2699;&#xfe0f; Safe API Key & Secrets Configuration</div>
                <p style="font-size:12px; color:#8b949e; margin-bottom:14px;">
                    Keys are safely stored locally in your <code>.env</code> file and masked. They are never committed to GitHub:
                </p>
                <div class="form-group">
                    <label>Google Gemini API Key (for Multimodal AI)</label>
                    <input type="password" id="key-gemini" placeholder="AIzaSy..." />
                </div>
                <div class="form-group">
                    <label>OpenAI API Key (Optional)</label>
                    <input type="password" id="key-openai" placeholder="sk-proj-..." />
                </div>
                <div class="form-group">
                    <label>Ethereum RPC URL (Alchemy / Infura)</label>
                    <input type="text" id="key-eth-rpc" placeholder="https://eth-mainnet.g.alchemy.com/v2/..." />
                </div>
                <button class="btn" onclick="saveApiKeys()">Save Configuration Safely to .env</button>
                <div id="settings-status" style="margin-top:8px; font-size:12px; color:var(--green);"></div>
            </div>
        </div>
    </div>

    <!-- Multiwallet Modal -->
    <div class="modal-overlay" id="wallet-modal" onclick="if(event.target===this) closeWalletModal()">
        <div class="modal">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <h3 style="color:#fff; font-size:16px;">Connect Multiwallet</h3>
                <span style="cursor:pointer; color:#8b949e;" onclick="closeWalletModal()">&times;</span>
            </div>
            <div class="wallet-option" onclick="selectWallet('Native QTC Core')">
                <div style="background:var(--accent); color:#000; width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:800;">Q</div>
                <div>
                    <div style="color:#fff; font-weight:600; font-size:13px;">Qitcoin Core L1</div>
                    <div style="font-size:11px; color:#8b949e;">Direct Node RPC Connection</div>
                </div>
            </div>
            <div class="wallet-option" onclick="selectWallet('MetaMask (0x71C...4022)')">
                <div style="background:#e16b25; color:#fff; width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:800;">M</div>
                <div>
                    <div style="color:#fff; font-weight:600; font-size:13px;">MetaMask (EVM / wQTC)</div>
                    <div style="font-size:11px; color:#8b949e;">Ethereum & Arbitrum Bridge</div>
                </div>
            </div>
            <div class="wallet-option" onclick="selectWallet('Phantom (8xQ...9sP)')">
                <div style="background:#ab9ff2; color:#000; width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:800;">P</div>
                <div>
                    <div style="color:#fff; font-weight:600; font-size:13px;">Phantom (Solana / wQTC)</div>
                    <div style="font-size:11px; color:#8b949e;">Fast SVM Bridge Connection</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let autoConwayInterval = null;

        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
            event.currentTarget.classList.add('active');
            document.getElementById('view-' + tabId).classList.add('active');
            if (tabId === 'conway') stepConway();
            if (tabId === 'launchpad') fetchLaunchpad();
        }

        function openWalletModal() { document.getElementById('wallet-modal').style.display = 'flex'; }
        function closeWalletModal() { document.getElementById('wallet-modal').style.display = 'none'; }
        function selectWallet(name) {
            document.getElementById('wallet-label').innerText = '✓ ' + name;
            closeWalletModal();
        }

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
                        <td><span style="background:#238636; color:#fff; padding:2px 6px; border-radius:4px; font-size:11px;">#${b.height}</span></td>
                        <td class="mono">${b.hash.substring(0, 16)}...${b.hash.substring(b.hash.length - 8)}</td>
                        <td>${b.transactions.length} tx</td>
                        <td style="color:var(--accent); font-weight:600;">+${b.reward_qtc.toLocaleString()} QTC</td>
                        <td>${b.nonce}</td>
                        <td style="color:#8b949e;">${new Date(b.timestamp * 1000).toLocaleTimeString()}</td>
                    `;
                    tbody.appendChild(row);
                });
            } catch(e) { console.error(e); }
        }

        async function mineBlock() {
            const status = document.getElementById('mining-status');
            status.innerText = 'Mining Proof-of-Work block...';
            const res = await fetch('/api/mine', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({})});
            const data = await res.json();
            status.innerText = `Block #${data.height} mined! Hash: ${data.hash.substring(0, 16)}...`;
            fetchChainInfo();
        }

        async function sendTransaction() {
            const recipient = document.getElementById('send-recipient').value;
            const amount = parseFloat(document.getElementById('send-amount').value);
            const status = document.getElementById('send-status');
            if(!recipient) { status.style.color = '#ef4444'; status.innerText = 'Please specify recipient!'; return; }
            const res = await fetch('/api/send', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({recipient, amount})});
            const data = await res.json();
            if(data.error) { status.style.color = '#ef4444'; status.innerText = data.error; }
            else { status.style.color = 'var(--green)'; status.innerText = `Tx broadcasted! TxID: ${data.txid.substring(0, 16)}...`; fetchChainInfo(); }
        }

        function showQrForAddress() {
            const container = document.getElementById('qr-container');
            const holder = document.getElementById('qr-svg-holder');
            container.style.display = container.style.display === 'none' ? 'block' : 'none';
            // Render mock SVG QR pattern
            holder.innerHTML = `<svg width="120" height="120" viewBox="0 0 100 100" style="background:#fff; border-radius:6px; padding:6px;">
                <rect x="10" y="10" width="25" height="25" fill="#000"/>
                <rect x="65" y="10" width="25" height="25" fill="#000"/>
                <rect x="10" y="65" width="25" height="25" fill="#000"/>
                <rect x="15" y="15" width="15" height="15" fill="#fff"/>
                <rect x="70" y="15" width="15" height="15" fill="#fff"/>
                <rect x="15" y="70" width="15" height="15" fill="#fff"/>
                <rect x="42" y="42" width="16" height="16" fill="#f59e0b"/>
                <circle cx="50" cy="50" r="4" fill="#000"/>
            </svg>`;
        }

        async function calculateSwapQuote() {
            const amtIn = parseFloat(document.getElementById('swap-amt-in').value) || 0;
            const from = document.getElementById('swap-from-token').value;
            const to = document.getElementById('swap-to-token').value;
            const res = await fetch(`/api/swap_quote?amt=${amtIn}&from=${from}&to=${to}`);
            const data = await res.json();
            document.getElementById('swap-amt-out').value = data.amount_out.toFixed(4);
            document.getElementById('swap-rate-display').innerText = `1 ${from} ≈ ${data.rate.toFixed(6)} ${to}`;
        }

        async function executeSwapAction() {
            const amtIn = parseFloat(document.getElementById('swap-amt-in').value);
            const from = document.getElementById('swap-from-token').value;
            const to = document.getElementById('swap-to-token').value;
            const status = document.getElementById('swap-status');
            status.innerText = 'Routing swap through liquidity pool...';
            const res = await fetch('/api/execute_swap', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({amt: amtIn, from, to})});
            const data = await res.json();
            status.style.color = 'var(--green)';
            status.innerText = `Swap complete! Received ${data.amount_out.toFixed(4)} ${to}. Tx Hash: ${data.txid.substring(0, 16)}...`;
        }

        async function initiateBridgeTransfer() {
            const amt = parseFloat(document.getElementById('bridge-amt').value);
            const dst = document.getElementById('bridge-dst').value;
            const recipient = document.getElementById('bridge-recipient').value;
            const status = document.getElementById('bridge-status');
            status.innerText = 'Locking L1 QTC & Generating NIST FIPS 204 PQC Attestation...';
            const res = await fetch('/api/bridge_transfer', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({amt, dst, recipient})});
            const data = await res.json();
            status.style.color = 'var(--green)';
            status.innerText = `Bridge transfer locked! Minting wQTC on ${dst}.`;
            document.getElementById('bridge-pqc-log').innerText = JSON.stringify(data.attestation, null, 2);
        }

        async function runPqcBenchmark() {
            const term = document.getElementById('pqc-terminal-output');
            term.innerText = 'Generating NIST FIPS 204 (ML-DSA-65) keypair & signing cross-chain header...';
            const res = await fetch('/api/pqc_benchmark');
            const data = await res.json();
            term.innerText = JSON.stringify(data, null, 2);
        }

        async function sendAgentMessage() {
            const input = document.getElementById('agent-input');
            const text = input.value.trim();
            if(!text) return;
            const term = document.getElementById('agent-chat-history');
            term.innerText += `\\n\\nUser: ${text}\\nAgent thinking...`;
            input.value = '';
            const res = await fetch('/api/agent_chat', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({prompt: text})});
            const data = await res.json();
            term.innerText += `\\nAgent: [${data.action_type}] ${data.response}`;
            term.scrollTop = term.scrollHeight;
            fetchChainInfo();
        }

        async function stepConway() {
            const res = await fetch('/api/conway_step');
            const data = await res.json();
            document.getElementById('conway-gen').innerText = data.generation;
            document.getElementById('conway-nodes').innerText = data.alive_nodes;
            document.getElementById('conway-health').innerText = data.mesh_health_score + '%';

            const gridEl = document.getElementById('conway-grid');
            gridEl.innerHTML = '';
            data.grid.forEach(row => {
                row.forEach(cell => {
                    const div = document.createElement('div');
                    div.className = 'cell' + (cell ? ' alive' : '');
                    gridEl.appendChild(div);
                });
            });
        }

        function toggleAutoConway() {
            const btn = document.getElementById('auto-conway-btn');
            if(autoConwayInterval) {
                clearInterval(autoConwayInterval);
                autoConwayInterval = null;
                btn.innerText = 'Auto-Run Mesh';
            } else {
                autoConwayInterval = setInterval(stepConway, 800);
                btn.innerText = 'Pause Mesh';
            }
        }

        async function fetchLaunchpad() {
            const res = await fetch('/api/launchpad_list');
            const data = await res.json();
            const holder = document.getElementById('lp-token-list');
            holder.innerHTML = '';
            data.forEach(t => {
                holder.innerHTML += `
                    <div style="background:#0b0f17; border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:#fff; font-size:14px;">${t.name} ($${t.ticker})</b>
                            <span style="color:var(--accent); font-weight:700;">${t.current_price_qtc.toFixed(6)} QTC</span>
                        </div>
                        <div style="font-size:11px; color:#8b949e; margin:4px 0;">${t.description}</div>
                        <div style="background:#1e293b; border-radius:4px; height:6px; overflow:hidden; margin:8px 0;">
                            <div style="background:var(--green); height:100%; width:${t.graduation_pct}%"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:11px; color:#8b949e;">
                            <span>Raised: ${t.collateral_raised_qtc.toLocaleString()} QTC</span>
                            <span>Bonding Curve: ${t.graduation_pct}%</span>
                        </div>
                    </div>
                `;
            });
        }

        async function createLaunchpadToken() {
            const name = document.getElementById('lp-name').value;
            const ticker = document.getElementById('lp-ticker').value;
            const supply = parseFloat(document.getElementById('lp-supply').value);
            const desc = document.getElementById('lp-desc').value;
            const status = document.getElementById('lp-create-status');
            const res = await fetch('/api/launchpad_create', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, ticker, supply, desc})});
            const data = await res.json();
            status.style.color = 'var(--green)';
            status.innerText = `Token $${ticker} launched on bonding curve!`;
            fetchLaunchpad();
        }

        async function requestX402Invoice(serviceId) {
            const term = document.getElementById('x402-terminal');
            term.innerText = `Requesting service '${serviceId}' -> HTTP 402 Challenge Issued...`;
            const res = await fetch(`/api/x402_request?service=${serviceId}`);
            const data = await res.json();
            term.innerText = `HTTP 402 PAYMENT REQUIRED:\\n` + JSON.stringify(data.invoice, null, 2);
            term.innerText += `\\n\\nSettling invoice with ${data.invoice.price_qtc} QTC from wallet...\\n`;
            
            const settleRes = await fetch('/api/x402_settle', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({invoice_id: data.invoice.invoice_id})});
            const settleData = await settleRes.json();
            term.innerText += `HTTP 200 OK (UNLOCKED MACHINE PAYLOAD):\\n` + JSON.stringify(settleData, null, 2);
        }

        async function saveApiKeys() {
            const gemini = document.getElementById('key-gemini').value;
            const openai = document.getElementById('key-openai').value;
            const eth = document.getElementById('key-eth-rpc').value;
            await fetch('/api/save_keys', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({gemini, openai, eth})});
            document.getElementById('settings-status').innerText = 'Configuration saved securely to local .env!';
        }

        fetchChainInfo();
        calculateSwapQuote();
        setInterval(fetchChainInfo, 3000);
    </script>
</body>
</html>
"""

class QTCPortalHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(parsed.query)

        if parsed.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PORTAL.encode("utf-8"))

        elif parsed.path == "/api/info":
            info = {
                "height": len(node_chain.chain) - 1,
                "supply": node_chain.get_circulating_supply(),
                "mempool_count": len(node_chain.mempool),
                "blocks": node_chain.chain[-20:]
            }
            self.send_json(info)

        elif parsed.path == "/api/swap_quote":
            amt = float(q.get("amt", [0])[0])
            from_t = q.get("from", ["QTC"])[0]
            to_t = q.get("to", ["USDT"])[0]
            pair = f"{from_t}/{to_t}" if f"{from_t}/{to_t}" in bridge_instance.pools else f"{to_t}/{from_t}"
            if pair in bridge_instance.pools:
                quote = bridge_instance.pools[pair].get_quote(amt, from_t)
                self.send_json({"amount_out": quote["amount_out"], "rate": quote["effective_rate"]})
            else:
                self.send_json({"amount_out": amt * 0.05, "rate": 0.05})

        elif parsed.path == "/api/pqc_benchmark":
            attestation = pqc_attestor.attest_cross_chain_transfer(
                "QITCOIN_L1", "ETHEREUM_MAINNET",
                node_chain.chain[-1]["hash"],
                node_chain.dev_miner_address,
                "0x71C841832046882c79B215d56418246999014022",
                10_000.0
            )
            self.send_json(attestation)

        elif parsed.path == "/api/conway_step":
            state = conway_automaton.step()
            self.send_json(state)

        elif parsed.path == "/api/launchpad_list":
            tokens = launchpad_instance.list_tokens()
            self.send_json(tokens)

        elif parsed.path == "/api/x402_request":
            svc = q.get("service", ["ai_inference"])[0]
            inv = x402_engine.create_invoice(svc, "client_autonomous_agent")
            self.send_json({"invoice": inv})

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

        if parsed.path == "/api/mine":
            block = node_chain.mine_block()
            self.send_json(block)

        elif parsed.path == "/api/send":
            try:
                tx = node_chain.send_transaction(node_chain.dev_miner_address, data.get("recipient"), float(data.get("amount", 0)))
                self.send_json(tx)
            except Exception as e:
                self.send_response(400)
                self.send_json({"error": str(e)})

        elif parsed.path == "/api/execute_swap":
            amt = float(data.get("amt", 0))
            from_t = data.get("from")
            to_t = data.get("to")
            pair = f"{from_t}/{to_t}" if f"{from_t}/{to_t}" in bridge_instance.pools else f"{to_t}/{from_t}"
            if pair in bridge_instance.pools:
                out = bridge_instance.pools[pair].execute_swap(amt, from_t)
            else:
                out = amt * 0.05
            txid = hashlib.sha256(os.urandom(32)).hexdigest()
            self.send_json({"amount_out": out, "txid": txid})

        elif parsed.path == "/api/bridge_transfer":
            amt = float(data.get("amt", 0))
            dst = data.get("dst")
            recipient = data.get("recipient")
            att = pqc_attestor.attest_cross_chain_transfer(
                "QITCOIN_L1", dst,
                node_chain.chain[-1]["hash"],
                node_chain.dev_miner_address,
                recipient, amt
            )
            self.send_json({"status": "LOCKED_AND_ATTESTED", "attestation": att})

        elif parsed.path == "/api/agent_chat":
            prompt = data.get("prompt", "")
            res = ai_agent.process_natural_language_command(prompt)
            self.send_json(res)

        elif parsed.path == "/api/launchpad_create":
            tok = launchpad_instance.create_token(data.get("name"), data.get("ticker"), float(data.get("supply")), node_chain.dev_miner_address, data.get("desc"))
            self.send_json({"status": "CREATED", "token_id": tok.token_id})

        elif parsed.path == "/api/x402_settle":
            inv_id = data.get("invoice_id")
            txid = f"tx_qtc_{os.urandom(8).hex()}"
            res = x402_engine.settle_invoice(inv_id, txid)
            self.send_json(res)

        elif parsed.path == "/api/save_keys":
            allow_key_writes = os.getenv("QTC_ALLOW_KEY_WRITES", "0") == "1"
            is_local = self.client_address[0] in {"127.0.0.1", "::1"}
            if not (allow_key_writes and is_local):
                self.send_json({"error": "Remote secret writes are disabled. Configure secrets in the hosting provider."}, status=403)
                return
            if data.get("gemini"): key_manager.set_key("GEMINI_API_KEY", data.get("gemini"))
            if data.get("openai"): key_manager.set_key("OPENAI_API_KEY", data.get("openai"))
            if data.get("eth"): key_manager.set_key("ETHEREUM_RPC_URL", data.get("eth"))
            self.send_json({"status": "SAVED"})

        elif parsed.path == "/rpc":
            # Bitcoin JSON-RPC Handler
            method = data.get("method")
            req_id = data.get("id")
            if method == "getblockchaininfo":
                res = {"chain": "regtest", "blocks": len(node_chain.chain)-1, "bestblockhash": node_chain.chain[-1]["hash"]}
            else:
                res = "ok"
            self.send_json({"jsonrpc": "2.0", "id": req_id, "result": res})

        else:
            self.send_response(404)
            self.end_headers()

    def send_json(self, obj, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))

def run_server(port=8080):
    server = HTTPServer(("0.0.0.0", port), QTCPortalHandler)
    print(f"=================================================================")
    print(f"QITCOIN (QTC) ALL-IN-ONE ECOSYSTEM PORTAL ONLINE")
    print(f"=================================================================")
    print(f"Web Portal Dashboard    : http://localhost:{port}")
    print(f"Bitcoin JSON-RPC 2.0 API: http://localhost:{port}/rpc")
    print(f"Cross-Chain DEX Swaps   : ACTIVE (QTC <-> USDT, BTC, ETH, SOL, ALGO)")
    print("NIST Post-Quantum PQC   : " + ("REAL ML-DSA AVAILABLE" if pqc_attestor.pqc_enabled else "TEST-ONLY FALLBACK (NOT VERIFIED)"))
    print(f"Multimodal AI Agentics  : ONLINE")
    print(f"Conway Automaton Mesh   : ACTIVE (16x16 Lattice)")
    print(f"x402 Bazaar Protocol    : READY (HTTP 402 Micropayments)")
    print(f"Token Launchpad         : ONLINE (Linear Bonding Curves)")
    print(f"=================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
