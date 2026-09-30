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


## Phase 2 — Local validation
- Build on Linux/Windows/macOS.
- Run unit + functional test suites.
- Launch 3-node regtest Docker topology.
- Mine, send, receive, restart, reindex, prune, backup/restore.

## Phase 3 — Private testnet
- 3+ geographically independent nodes.
- Explorer + faucet.
- Difficulty, propagation, reorg and wallet recovery tests.

## Phase 4 — Public testnet
- Public binaries + signed checksums.
- DNS seeds, docs, telemetry and incident process.
- External security review and bug bounty.

## Phase 5 — Mainnet readiness
- Release candidate freeze.
- Reproducible builds.
- Genesis procedure.
- Legal/compliance review.
- Mainnet launch only after explicit signoff.
