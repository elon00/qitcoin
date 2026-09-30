# Qitcoin (QTC) Production Mainnet Deployment Masterplan

This masterplan details the rigorous, phased deployment process for launching Qitcoin onto public mainnet.

---

## 1. Phased Deployment Timeline

```
[Phase 0: Specifications & Supply Freeze] (COMPLETE)
                   |
                   v
[Phase 1: Regtest & Localhost Verification] (LIVE NOW on http://localhost:8080)
                   |
                   v
[Phase 2: Private Multi-Node Testnet] (3-5 Controlled Validator Nodes)
                   |
                   v
[Phase 3: Public Testnet + Faucet + Explorer] (Community Testing & Bug Bounty)
                   |
                   v
[Phase 4: Security Audit, PQC Verification & Release Candidate Freeze]
                   |
                   v
[Phase 5: Mainnet Genesis Ceremony & Global Public Launch]
```

---

## 2. Infrastructure Setup for Mainnet

### Step 1: Global Seed Node Topology
A decentralized network requires initial bootstrap peers (DNS seeds and static IPs).
Deploy **3 to 5 geographically distributed VPS instances** (Ubuntu 24.04 LTS, 4 vCPU, 8GB RAM, 200GB SSD):
* **Seed 1**: US East (North Virginia) — `seed1.qitcoin.org:19333`
* **Seed 2**: Europe (Frankfurt) — `seed2.qitcoin.org:19333`
* **Seed 3**: Asia-Pacific (Singapore) — `seed3.qitcoin.org:19333`
* **Seed 4**: Latin America (São Paulo) — `seed4.qitcoin.org:19333`

Configure DNS seed record:
`dnsseed.qitcoin.org -> A records of all 4 seed node IPs`.

### Step 2: Mining Pool Setup (Stratum Protocol)
Deploy open-source mining pool software (e.g. `yiimp` or `nomp` adapted for QTC SHA-256d):
* Stratum port: `3333`
* Payout threshold: 1,000 QTC
* Difficulty target: Variable (vardiff)

### Step 3: Production Block Explorer & Indexer
* Deploy public block explorer (e.g. BTC-RPC-Explorer or Blockbook adapted for QTC 6 decimals).
* Expose public JSON-RPC endpoints with rate-limiting via Cloudflare / Nginx.

---

## 3. Mainnet Launch Ceremony Checklist

1. [ ] **Code Freeze**: Pin upstream release tag and freeze all consensus patches.
2. [ ] **Genesis Ceremony**:
   - Collect major news headline on launch morning for `pszTimestamp`.
   - Run `python tools/genesis_miner.py` to mine mainnet nonce and hash.
   - Embed genesis hash into `src/chainparams.cpp`.
3. [ ] **Reproducible Binaries (Guix Build)**:
   - Compile deterministic, bit-for-bit identical binaries across Linux, Windows, and macOS.
   - Collect GPG signatures from multiple core contributors.
4. [ ] **Bootstrap Mining Nodes**:
   - Start 3 seed nodes simultaneously with mainnet binary.
   - Mine Block #1 to ensure network difficulty adjusts correctly.
5. [ ] **Publish Public Binaries & Source**:
   - Release binaries on GitHub Releases with SHA-256 checksums.
   - Publish live Block Explorer and Faucet.
