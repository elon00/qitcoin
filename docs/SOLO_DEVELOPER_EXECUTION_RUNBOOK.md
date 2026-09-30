# Solo Developer Execution Runbook: From Native Core Build to Mainnet Readiness

> **Target Sequence**: `Native Core Build` $\to$ `Regtest` $\to$ `3-Node Native Testnet` $\to$ `Wallet / Consensus / Security Tests` $\to$ `Release Binaries` $\to$ `Public Soak` $\to$ `Mainnet Readiness`.

This runbook is the definitive tactical roadmap for a solo engineer to take Qitcoin (QTC) from the current repository state all the way to production readiness without needing a large team.

---

## 1. What a Solo Developer Truly Owns vs. External Validation

| Category | Component | Solo Developer Ownership | External Dependency (Not a Code Blocker) |
|---|---|---|---|
| **Consensus Core** | `qitcoind`, `qitcoin-cli`, consensus patches | 100% Solo Ownable | None |
| **Testing** | Unit, Functional, Reorg, Reindex, Prune tests | 100% Solo Ownable | None |
| **Sanitizers & Fuzzing** | ASan, UBSan, TSan, AFL/libFuzzer runs | 100% Solo Ownable | None |
| **Infrastructure** | 3-node testnet, DNS seeds, static fallbacks | 100% Solo Ownable | \$0 – \$15/mo VPS budget |
| **Tooling** | Faucet, Block Explorer, Desktop Wallet, RPC | 100% Solo Ownable | None |
| **CI/CD & Releases** | Multi-platform compilation, signed releases | 100% Solo Ownable | GitHub Actions Compute |
| **External Security** | Formal 3rd-party audit (e.g. Trail of Bits) | Preparation & bug bounty triage | External firm sign-off |
| **Compliance** | Jurisdiction-specific securities legal opinion | Clean open-source MIT structure | External legal counsel |
| **Exchanges** | Centralized exchange listings (Binance, Bybit) | Standalone node & Rosetta API support | Listing team approval |

---

## 2. Step-by-Step Technical Execution Sequence

```
[1. GitHub Actions CI Build]
      │ Compiles native C++ qitcoind & qitcoin-cli (Ubuntu & Windows)
      ▼
[2. Local Docker 3-Node Regtest]
      │ Runs node1 (seed), node2 (relay), node3 (wallet) on local machine
      ▼
[3. Multi-Node Functional Tests]
      │ Executes test_qitcoin_3nodes.py (Maturity, Reorgs, Wallet Restore)
      ▼
[4. Deploy 3 Persistent Cloud Nodes]
      │ Oracle Cloud Free Tier / Hetzner VPS ($4/mo) worldwide
      ▼
[5. Public Testnet Launch & Soak Period]
      │ Faucet + Explorer live; 10,000 continuous blocks mined
      ▼
[6. Signed Release Candidate (RC1)]
      │ Git tagged releases with SHA-256 checksums
      ▼
[7. Mainnet Readiness Ceremony]
      │ Mainnet genesis mined with launch headline; public seed launch
```

---

## 3. Step 1: Native Core Compilation via GitHub Actions

Because compiling Bitcoin Core C++ on local Windows requires complex MSYS2/WSL configurations, the repository includes **`.github/workflows/build-qitcoin-core.yml`**.

1. Go to your GitHub repository: [https://github.com/elon00/qitcoin/actions](https://github.com/elon00/qitcoin/actions)
2. Click **Build Native Qitcoin Core** $\to$ **Run workflow**.
3. GitHub's free runners will:
   * Clone Bitcoin Core pinned release (`v27.1`).
   * Apply all 4 Qitcoin consensus patches (`01` through `04`).
   * Run `./autogen.sh && ./configure && make -j$(nproc)`.
   * Run unit tests (`make check`).
   * Produce downloadable native binaries: `qitcoind` and `qitcoin-cli`.

---

## 4. Step 2 & 3: 3-Node Docker Topology & Functional Tests

On your local laptop or workstation:

```powershell
cd c:\Users\marti\Downloads\bountyhunter-os-main\qitcoin

# Build and start the 3-node cluster in the background
docker-compose up -d

# Check cluster logs
docker-compose logs -f

# Run the 3-node functional test suite
python test/functional/test_qitcoin_3nodes.py
```

### What this validates:
* **Node 1** (Seed) handshakes with **Node 2** and **Node 3**.
* 101 blocks mined on Node 1 propagate instantly to Node 2 and Node 3.
* 5,000 QTC transaction relays across mempools without consensus deviation.
* Reorganization depth limits prevent deep 51% reorg attacks.

---

## 5. Step 4: Deploying 3 Persistent Public Testnet Nodes

To transition from local Docker to a persistent public testnet:

### Cost-Effective Infrastructure Blueprint:
1. **Node 1 (US East)**: **Oracle Cloud "Always Free" Tier** (Up to 4 Ampere ARM cores + 24GB RAM free forever).
2. **Node 2 (Europe - Frankfurt)**: **Hetzner Cloud CX22** (€3.79/month).
3. **Node 3 (Asia - Singapore)**: **Contabo / Vultr VPS** (\$5.00/month).

### Deployment on Each Node:
```bash
# Clone Qitcoin on the VPS
git clone https://github.com/elon00/qitcoin.git
cd qitcoin

# Build and start via Docker
docker-compose -f docker-compose.yml up -d node1
```

### DNS Seed Configuration:
* Purchase a domain (e.g. `qitcoin.network` or `qitcoin.org`).
* Create DNS `A` records for `seed.qitcoin.org` pointing to all 3 VPS IP addresses.
* New community nodes that start with `-testnet` will query `seed.qitcoin.org` and automatically discover peers.

---

## 6. Step 5: Public Soak Testing Gate

Before declaring mainnet readiness, the public testnet must satisfy these non-negotiable gates:
* [ ] **Continuous Block Production**: $\ge 10,000$ blocks mined without stall.
* [ ] **Memory Stability**: Zero memory leaks (`valgrind` / ASan clean over 7 days).
* [ ] **Reindex Sanity**: `qitcoind -reindex` completes from scratch without block validation errors.
* [ ] **Pruning Test**: `qitcoind -prune=550` operates cleanly with reduced disk usage.
* [ ] **Wallet Recovery**: BIP39 12/24-word seed restore re-derives identical addresses and UTXO balance.

---

## 7. Step 6 & 7: Mainnet Genesis Ceremony

Once the soak test passes:
1. Choose the launch date morning newspaper headline (e.g. *"The Times [Date] [Headline]"*).
2. Run `python tools/genesis_miner.py` to mine the mainnet nonce and hash.
3. Update `patches/04_genesis_block.patch` with the final mainnet hash.
4. Cut Git release tag `v1.0.0` on GitHub.
5. Launch the seed nodes with the mainnet binary.
6. The decentralized 1 Trillion QTC economy is live.
