# Qitcoin (QTC) End-to-End Technical Solutions & Architecture Blueprint

This document details the comprehensive engineering solutions, mathematical proofs, security mitigations, and operational blueprint for launching **Qitcoin (QTC)** as a standalone Layer-1 Proof-of-Work cryptocurrency with a maximum supply of **1 Trillion QTC**.

---

## 1. The 1 Trillion Supply Challenge & The Int64 Mathematical Solution

### The Core Problem in Bitcoin Core
Bitcoin Core implements all monetary accounting using `CAmount`, which is an alias for signed 64-bit integer (`int64_t`).
- Maximum possible value in `int64_t`: `2^63 - 1 = 9,223,372,036,854,775,807` (~9.22 × 10^18 base units).
- In standard Bitcoin: Max supply = 21,000,000 BTC. Base unit = 10^-8 (1 satoshi).
  - Total Satoshis = `21,000,000 * 10^8 = 2,100,000,000,000,000 = 2.1 * 10^15`.
  - Fits easily inside `int64_t`.

If a developer naively sets Bitcoin Core's max supply to 1 Trillion (1,000,000,000,000) while keeping 8 decimal places:
- Total Base Units = `1,000,000,000,000 * 10^8 = 100,000,000,000,000,000,000 = 10^20`.
- **10^20 exceeds `9.22 * 10^18` by more than 10x!**
- **Fatal Outcome**: Integer overflow in C++, catastrophic negative balances, consensus crashes, and unbounded coin duplication.

### The Qitcoin Engineering Solution: 6 Decimals (`qits`)
Qitcoin defines its base currency unit as the **`qit`**, with **6 decimal places** (`1 QTC = 1,000,000 qits`):
- `Total Base Units = 1,000,000,000,000 QTC * 1,000,000 qits/QTC = 1,000,000,000,000,000,000 qits = 10^18 qits`.
- `1.0 * 10^18 < 9.22 * 10^18`.
- **Safety Headroom**: 89.16% remaining capacity in `int64_t`.
- **Result**: Complete mathematical safety across all transaction validation, UTXO balances, fee calculations, and memory pools.

```cpp
// src/consensus/amount.h
static constexpr CAmount COIN = 1000000; // 1 QTC = 1,000,000 qits (6 decimals)
static constexpr CAmount CENT = 10000;
static constexpr CAmount MAX_MONEY = 1000000000000LL * COIN; // 10^18 qits
inline bool MoneyRange(const CAmount& nValue) { return (nValue >= 0 && nValue <= MAX_MONEY); }
```

---

## 2. Subsidy Schedule & Mathematical Cap Proof

To guarantee that total issuance will never exceed 1,000,000,000,000 QTC, Qitcoin uses a geometric halving schedule:
- **Block Interval**: 60 seconds (1 minute).
- **Halving Interval**: 2,000,000 blocks (~3.80 years).
- **Initial Subsidy**: 250,000 QTC per block.

### Exact Halving Table
$$\text{Total Issuance} = \sum_{i=0}^{37} \lfloor 250,000 \cdot 10^6 \gg i \rfloor \cdot 2,000,000 = 999,999,999,974\text{ QTC}$$

| Era | Block Range | Block Subsidy (QTC) | Era Total Mined (QTC) | Cumulative Total (QTC) | % of Cap |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **0** | 0 – 1,999,999 | 250,000.0000 | 500,000,000,000.00 | 500,000,000,000.00 | 50.00% |
| **1** | 2,000,000 – 3,999,999 | 125,000.0000 | 250,000,000,000.00 | 750,000,000,000.00 | 75.00% |
| **2** | 4,000,000 – 5,999,999 | 62,500.0000 | 125,000,000,000.00 | 875,000,000,000.00 | 87.50% |
| **3** | 6,000,000 – 7,999,999 | 31,250.0000 | 62,500,000,000.00 | 937,500,000,000.00 | 93.75% |
| **4** | 8,000,000 – 9,999,999 | 15,625.0000 | 31,250,000,000.00 | 968,750,000,000.00 | 96.875% |
| **5** | 10,000,000 – 11,999,999 | 7,812.5000 | 15,625,000,000.00 | 984,375,000,000.00 | 98.437% |
| ... | ... | ... | ... | ... | ... |
| **37**| 74,000,000 – 75,999,999| 0.000001 | 2.00 | 999,999,999,974.00 | 99.9999% |
| **38+**| 76,000,000+ | 0.000000 | 0.00 | **999,999,999,974.00** | 100.00% |

- **Verification**: `python tools/verify_supply.py` programmatically tests and asserts this cap.

---

## 3. Network Parameters & Mined Genesis Block

### Mined Genesis Parameters
- **Coinbase Message**: `"The Times 30/Sep/2026 Qitcoin: The Decentralized Trillion Economy"`
- **Genesis Public Key**: Standard uncompressed secp256k1 key.
- **Merkle Root**: `9a5bcf89553e6cc933455c84a964f720f0aa47628f5bfee08e0db920a37db79a`

```cpp
// Mainnet Genesis Block
CreateGenesisBlock(1790772000, 388903, 0x1e0ffff0, 1, 250000 * COIN);
// Hash: 0x0000064d6898cab247cd7a66ae5d621abe9decd284d84b8a1b857b0606dc532a

// Regtest Genesis Block
CreateGenesisBlock(1790772000, 1, 0x207fffff, 1, 250000 * COIN);
// Hash: 0x3e1630837eda1b40c16c84d5adf7f86b89707a5c63326968f5436c30bc6c2407
```

### Network Identifiers
- **P2P Port**: `19333` (Mainnet), `29333` (Testnet), `39333` (Regtest)
- **RPC Port**: `19332` (Mainnet), `29332` (Testnet), `39332` (Regtest)
- **Magic Bytes**:
  - Mainnet: `0x71 0x74 0x63 0x01` (`qtc\x01`)
  - Testnet: `0x71 0x74 0x63 0x02` (`qtc\x02`)
  - Regtest: `0x71 0x74 0x63 0x03` (`qtc\x03`)
- **Address Encodings**:
  - Standard P2PKH: Prefix `Q` (`base58Prefixes[PUBKEY_ADDRESS] = 58`)
  - Standard P2SH: Prefix `T` (`base58Prefixes[SCRIPT_ADDRESS] = 65`)
  - Native SegWit / Bech32 HRP: `qtc` (e.g. `qtc1q...`)

---

## 4. 51% Attack Defense for a New PoW Blockchain

A new PoW chain starting with SHA-256d is vulnerable to 51% reorg attacks because any small fraction of existing Bitcoin ASIC miners could overpower the new network.

### Multi-Tier Defense Strategy:
1. **Initial Phased Rollout**:
   - Begin strictly on private testnet and public testnet.
2. **Rolling Checkpointing (Preventing Deep Reorgs)**:
   - Configure nodes to reject reorgs deeper than 50 blocks:
     `maxReorgDepth = 50;`
3. **ChainLock / Notarization Integration**:
   - Include periodic hardcoded block checkpoints in point releases.
4. **Phase 2 Hard Fork to ASIC-Resistant Algorithm or AuxPoW**:
   - If standalone SHA-256d hashrate remains modest, execute planned hard-fork to **AuxPoW** (Merged Mining with Bitcoin so Bitcoin miners mine Qitcoin for free without diverting hashpower) OR **RandomX** (CPU-only mining allowing thousands of everyday community members to run decentralized nodes and mine).

---

## 5. Solo Developer Step-by-Step Execution Plan

Can a solo developer build, run, and publish this? **Yes.** Here is the lean solo developer playbook:

### Step 1: Local Development & Verification (Completed in Repo!)
- Run the interactive localhost node & Block Explorer on `http://localhost:8080`.
- Verify mining, wallet creation, transaction broadcasting, and RPC calls.
- Inspect the patches and supply verification scripts.

### Step 2: Push to GitHub & CI/CD Cross-Compilation
- Create a new repository on GitHub: `https://github.com/<your-username>/qitcoin`.
- Push this codebase to the repository.
- Use GitHub Actions (`.github/workflows/`) to cross-compile binary releases:
  - `qitcoind` and `qitcoin-cli` for Ubuntu Linux (`x86_64`)
  - `qitcoind.exe` and `qitcoin-cli.exe` for Windows 64-bit
  - macOS binaries (`arm64` Apple Silicon).

### Step 3: Launch 3 Public Seed Nodes
- Rent 3 modest cloud VPS servers ($5–$10/mo each) across separate regions:
  - Node 1: US East (e.g., Virginia)
  - Node 2: Europe (e.g., Frankfurt)
  - Node 3: Asia (e.g., Singapore)
- Run `qitcoind -testnet` on all 3 nodes.
- Set up a DNS seed domain (e.g., `seed.qitcoin.org`) pointing to these IPs.

### Step 4: Public Testnet Faucet & Explorer
- Run the web-based explorer connected to the testnet seed node.
- Provide a faucet webpage where users can paste their `Q...` address and receive 1,000 QTC to test wallets and transactions.

### Step 5: Community Wallet & Release
- Package Electrum-QTC (Python desktop wallet) or release pre-compiled `qitcoin-qt`.
- Release binaries with GPG signed hashes on GitHub Releases.
