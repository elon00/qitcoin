# Qitcoin Development Roadmap & Live Status Manifest

> **Ground-Truth Tracking**: Each milestone is updated only upon verifiable proof. Mock simulation fallbacks are strictly prohibited.

---

## Current Status Overview

```
[Phase 0: Specification]                  ✅ COMPLETED (Frozen)
[Phase 1: Native Core Build]              ✅ COMPLETED & VERIFIED (Artifact: 31301620...)
[Phase 2: 3-Node Topology Validation]     🔄 READY FOR EXECUTION (Strict test suite, no mocks)
[Phase 3: Public Testnet Infrastructure]  🔄 TOOLING READY (Native qitcoind VPS installer)
[Phase 4: Release Automation & Soak]      🔄 PIPELINE READY (Pending 10,000-block soak)
[Phase 5: Mainnet Genesis & Launch]       ⏳ PENDING (Gated on Phase 4 soak signoff)
```

---

## Phase 0 — Specification [COMPLETED]
- [x] Freeze name/ticker/decimals/supply: Qitcoin (QTC), 1 Trillion max supply, 6 decimals (`qits`).
- [x] Decide PoW/difficulty/block interval/subsidy schedule: SHA-256d, 60s block spacing, 250k initial reward, 2M halving.
- [x] Define testnet/mainnet address prefixes and ports: P2P `19333`, RPC `19332`, Base58 `Q`/`T`, Bech32 `qtc`.

## Phase 1 — Fork Engineering & Native Core Build [COMPLETED & VERIFIED]
- [x] Import pinned Bitcoin Core upstream release (`v27.1`).
- [x] Implement 6-decimal monetary range (`MAX_MONEY = 10^18 qits`) with int64 safety proof.
- [x] Implement 250,000 QTC block subsidy schedule strictly capping to 999,999,999,974 QTC.
- [x] Generate unique genesis block with *"The Times 30/Sep/2026 Qitcoin"* timestamp.
- [x] **Native Build Verified**: GitHub Actions Build #36740554378 passed.
  * Artifact: `qitcoin-core-linux-x86_64` (~109 MB)
  * SHA-256 Digest: `313016203f80ecb7c627426992dd6a3e70398cfca2d7ac8da74bbdf0fd5580ad`
  * Binaries: `qitcoind` and `qitcoin-cli` compiled and unit-tested.

## Phase 2 — 3-Node Topology Validation [TOOLING READY / IN EXECUTION]
- [x] Multi-platform compilation workflow (`.github/workflows/build-qitcoin-core.yml`).
- [x] Strict 3-node functional test suite without mock simulation (`test/functional/test_qitcoin_3nodes.py`).
- [x] 3-node isolated Docker topology (`docker-compose.yml`, `docker/Dockerfile.qitcoind`).
- [x] CI workflow for automated cluster testing (`.github/workflows/test-3node-cluster.yml`).
- [ ] Live cluster execution verification: 101-block maturity, mempool sync, 50-block reorg limit.

## Phase 3 — Public Testnet Infrastructure [TOOLING READY / PENDING HOSTING]
- [x] Native VPS seed installer script running `qitcoind.service` (`scripts/deploy-testnet-seed.sh`).
- [x] Static seed fallback and DNS seed configuration guide.
- [x] Testnet Faucet endpoint (`/api/faucet`) and block explorer.
- [x] Multichain Bridge (HTLC + TSS-MPC) and NIST FIPS 204 PQC verifier engine.
- [ ] Deployment of 3 persistent public testnet VPS nodes (Oracle Always Free / Hetzner).
- [ ] DNS seed `seed.qitcoin.org` pointing to live public testnet IPs.

## Phase 4 — Release Automation & Public Soak [PIPELINE READY / SOAK PENDING]
- [x] Self-contained release workflow building native binaries and attaching real tarballs (`.github/workflows/release.yml`).
- [x] Release packaging scripts for Linux (`scripts/package-release.sh`) and Windows (`scripts/package-release.ps1`).
- [x] Web 4.0 x402 Bazaar Protocol and Conway AI Automaton mesh.
- [x] Flutter & Serverpod cross-platform wallet application.
- [ ] **Public Soak Test Gate**: $\ge 10,000$ continuous blocks mined on public testnet without memory leak or desync.
- [ ] 7-day sanitizer stability (ASan/UBSan) and wallet restore verification.

## Phase 5 — Mainnet Readiness & Launch [PENDING SOAK PASS]
- [x] Official Genesis Ceremony cryptographic record (`docs/GENESIS_CEREMONY_RECORD.md`).
- [x] Mainnet Genesis Mined: `0x0000064d6898cab247cd7a66ae5d621abe9decd284d84b8a1b857b0606dc532a` (Nonce: `388903`).
- [x] Solo Developer Execution Runbook (`docs/SOLO_DEVELOPER_EXECUTION_RUNBOOK.md`).
- [ ] Formal launch ceremony with morning news headline embedding.
- [ ] Signed `v1.0.0` mainnet release publication.
