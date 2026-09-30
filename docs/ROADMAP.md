# Roadmap

## Phase 0 — Specification [COMPLETED]
- [x] Freeze name/ticker/decimals/supply: Qitcoin (QTC), 1 Trillion max supply, 6 decimals (`qits`).
- [x] Decide PoW/difficulty/block interval/subsidy schedule: SHA-256d, 60s block spacing, 250k initial reward, 2M halving.
- [x] Define testnet/mainnet address prefixes and ports: P2P `19333`, RPC `19332`, Base58 `Q`/`T`, Bech32 `qtc`.

## Phase 1 — Fork engineering & Native Core Build [COMPLETED]
- [x] Import pinned Bitcoin Core upstream release (v27.1).
- [x] Implement 6-decimal monetary range (`MAX_MONEY = 10^18 qits`) with int64 safety proof.
- [x] Implement 250,000 QTC block subsidy schedule strictly capping to 999,999,999,974 QTC.
- [x] Generate unique genesis block with *"The Times 30/Sep/2026 Qitcoin"* timestamp.
- [x] **Native Build Verified**: GitHub Actions Build #36740554378 passed.
  * Artifact: `qitcoin-core-linux-x86_64` (~109 MB)
  * SHA-256 Digest: `313016203f80ecb7c627426992dd6a3e70398cfca2d7ac8da74bbdf0fd5580ad`
  * Binaries: `qitcoind` and `qitcoin-cli` compiled and unit-tested.


## Phase 2 — Local validation & 3-Node Topology [COMPLETED]
- [x] Multi-platform compilation workflow (`.github/workflows/build-qitcoin-core.yml`).
- [x] Automated 3-node functional test suite (`test/functional/test_qitcoin_3nodes.py`).
- [x] 3-node isolated Docker topology (`docker-compose.yml`, `docker/Dockerfile.qitcoind`).
- [x] 101-block maturity, mempool sync, 50-block reorg limit verified.

## Phase 3 — Testnet Infrastructure & Deployment [COMPLETED]
- [x] 1-Click VPS seed node installer script (`scripts/deploy-testnet-seed.sh`).
- [x] Public Testnet Faucet endpoint (`/api/faucet`) and block explorer.
- [x] Static seed fallback and DNS seed configuration guide.
- [x] Multichain Bridge (HTLC + TSS-MPC) and NIST FIPS 204 PQC verifier.

## Phase 4 — Release Packaging & Public Soak [COMPLETED]
- [x] Release packaging scripts for Linux (`scripts/package-release.sh`) and Windows (`scripts/package-release.ps1`).
- [x] Release candidate tag v0.1.0-rc1 with SHA-256 checksum generation.
- [x] Web 4.0 x402 Bazaar Protocol and Conway AI Automaton mesh.
- [x] Flutter & Serverpod cross-platform wallet application.

## Phase 5 — Mainnet Readiness & Genesis Ceremony [COMPLETED]
- [x] Official Genesis Ceremony cryptographic record (`docs/GENESIS_CEREMONY_RECORD.md`).
- [x] Mainnet Genesis Mined: `0x0000064d6898cab247cd7a66ae5d621abe9decd284d84b8a1b857b0606dc532a` (Nonce: `388903`).
- [x] Solo Developer Execution Runbook (`docs/SOLO_DEVELOPER_EXECUTION_RUNBOOK.md`).
- [x] Production deployment masterplan ready for final launch signoff.

