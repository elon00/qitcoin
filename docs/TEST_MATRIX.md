# Test Matrix

- Consensus: subsidy boundaries, max-money, invalid blocks, reorgs, timestamps, difficulty.
- P2P: handshake isolation, magic bytes, ports, malformed peers, ban logic.
- Wallet: create, restore, encrypt, backup, descriptors, send/receive, fee bump, PSBT.
- Node: IBD, restart, reindex, prune, RPC auth, ZMQ if enabled.
- Network: 1/3/10 node topologies, partitions, latency, reconnection, fork resolution.
- Security: ASan/UBSan/TSan where applicable, fuzzers, dependency review, RPC exposure review.
- Release: deterministic artifacts, signatures, checksums, upgrade/rollback procedure.
