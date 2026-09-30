# Qitcoin Core (QTC) 🚀

> **A Bitcoin-Core-derived standalone Layer-1 Proof-of-Work blockchain designed for a 1 Trillion Max Supply digital economy.**

---

## ⚡ Quick Specs & Consensus Target

| Parameter | Specification | Consensus Engineering Rationale |
|---|---|---|
| **Name** | Qitcoin | Standalone Layer-1 Blockchain |
| **Ticker** | **QTC** | Native Currency Symbol |
| **Max Supply** | **1,000,000,000,000 QTC** | Fixed Hard-Cap (1 Trillion) |
| **Base Currency Unit** | **`qit`** (`10^-6 QTC`) | 6 Decimal Places |
| **Base Units Cap** | **1,000,000,000,000,000,000 qits** | $10^{18}$ fits strictly in `int64_t` ($9.22 \times 10^{18}$ limit) |
| **Consensus Algorithm** | Proof-of-Work (PoW) | Double SHA-256d |
| **Target Block Interval**| **60 seconds** (1 minute) | Fast confirmations for local & global usage |
| **Initial Block Reward** | **250,000 QTC** per block | Halves every 2,000,000 blocks (~3.8 years) |
| **Total Halving Eras** | 38 Eras | Total mined = 999,999,999,974 QTC ($\le 1$ Trillion) |
| **Address Prefixes** | **Q** (P2PKH), **T** (P2SH), **qtc** (Bech32) | Distinct network identification |
| **Network Ports** | P2P: `19333`, RPC: `19332` | Non-conflicting standard ports |

---

## 🖥️ 1-Click Localhost Interactive Node & Block Explorer

You can test Qitcoin right now on your computer! We have built a zero-dependency local node and block explorer with PoW mining, UTXO ledger, mempool, wallet, and Bitcoin-compatible JSON-RPC:

### To Launch:
Double-click `start_localhost_node.bat` or run:
```powershell
python localhost_node/server.py 8080
```

### Access Points:
- **Web Block Explorer & Wallet Dashboard**: [http://localhost:8080](http://localhost:8080)
- **Bitcoin JSON-RPC 2.0 API**: `http://localhost:8080/rpc`

You can click **"Mine 1 New Block"**, generate new `Q...` addresses, send transactions, and watch blocks propagate live!

---

## 🛠️ Verification & Genesis Tools

### 1. Verify 1 Trillion Supply & Int64 Safety
Programmatically verifies that total mined coins across all 38 halving eras never exceed 1,000,000,000,000 QTC and never overflow signed 64-bit integer limits:
```powershell
python tools/verify_supply.py
```

### 2. Mine Genesis Blocks
Generates and mines custom Genesis blocks for Mainnet, Testnet, and Regtest with custom timestamp phrase:
```powershell
python tools/genesis_miner.py
```

---

## 📦 Consensus Patches (`patches/`)

Ready-to-apply patches for the Bitcoin Core C++ codebase:
1. [`patches/01_amount_and_maxmoney.patch`](file:///c:/Users/marti/Downloads/bountyhunter-os-main/qitcoin/patches/01_amount_and_maxmoney.patch) — Changes `COIN = 1,000,000` (6 decimals) and `MAX_MONEY = 10^18 qits` (1 Trillion QTC).
2. [`patches/02_subsidy_and_halving.patch`](file:///c:/Users/marti/Downloads/bountyhunter-os-main/qitcoin/patches/02_subsidy_and_halving.patch) — Implements 250,000 QTC initial subsidy and 2,000,000 block halving interval.
3. [`patches/03_chainparams_and_network.patch`](file:///c:/Users/marti/Downloads/bountyhunter-os-main/qitcoin/patches/03_chainparams_and_network.patch) — Configures ports (`19333`/`19332`), magic bytes, 1-min block spacing, and address prefixes (`Q`/`T`/`qtc`).
4. [`patches/04_genesis_block.patch`](file:///c:/Users/marti/Downloads/bountyhunter-os-main/qitcoin/patches/04_genesis_block.patch) — Integrates mined Genesis blocks and unique timestamp.

---

## 📚 Complete Documentation & Guides

- **[End-to-End Solutions & Blueprint](file:///c:/Users/marti/Downloads/bountyhunter-os-main/qitcoin/docs/END_TO_END_SOLUTIONS.md)**: Deep dive into 51% attack mitigation, seed nodes, int64 math, and solo developer execution strategy.
- **[GitHub Setup & CI/CD Guide](file:///c:/Users/marti/Downloads/bountyhunter-os-main/qitcoin/docs/GITHUB_SETUP.md)**: Step-by-step instructions to create the GitHub repository and push code.
- **[Coin Specification](file:///c:/Users/marti/Downloads/bountyhunter-os-main/qitcoin/docs/COIN_SPEC.md)**: Parameters and design constraints.
- **[Development Roadmap](file:///c:/Users/marti/Downloads/bountyhunter-os-main/qitcoin/docs/ROADMAP.md)**: From Regtest to Audited Mainnet.
- **[Testing Matrix](file:///c:/Users/marti/Downloads/bountyhunter-os-main/qitcoin/docs/TEST_MATRIX.md)**: Test criteria for consensus, nodes, and wallets.

---

## 🔒 Safety & Mainnet Gate

- Do not launch a public mainnet with real user funds until thorough public testnet soaking, peer review, reproducible builds, and multi-region seed node deployment are concluded.
