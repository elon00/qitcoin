# Roadmap

## Phase 0 — Specification
- Freeze name/ticker/decimals/supply.
- Decide PoW/difficulty/block interval/subsidy schedule.
- Define testnet/mainnet address prefixes and ports.

## Phase 1 — Fork engineering
- Import pinned Bitcoin Core upstream release.
- Apply branding and build-system changes.
- Implement 6-decimal amount display and monetary range.
- Generate unique genesis/network constants.
- Add consensus tests.

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
