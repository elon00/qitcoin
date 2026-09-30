# Qitcoin End-to-End Blueprint

## 1. Product layers
1. Consensus: PoW, block validation, subsidy, difficulty, chain selection.
2. P2P network: magic bytes, ports, peers, DNS seeds, addrman.
3. Ledger: UTXO model, transactions, fees, mempool.
4. Wallet: HD wallet, descriptors, backup/recovery, PSBT.
5. Node/RPC: qitcoind, qitcoin-cli, REST/RPC authentication.
6. Developer stack: regtest, testnet, Docker, CI, fuzzing.
7. User stack: desktop wallet/Qt, optional web explorer and faucet for testnet.
8. Operations: seed nodes, monitoring, releases, incident response.

## 2. Network progression
- Regtest: deterministic local development, no public value.
- Private testnet: controlled multi-node compatibility tests.
- Public testnet: faucet, explorer, public seed nodes.
- Mainnet: only after release candidate audit and launch checklist signoff.

## 3. Required Bitcoin Core source changes
- Branding: executable/package/help text where technically appropriate.
- Currency unit / display decimals.
- `MAX_MONEY` and money-range validation.
- Block subsidy function and exact cap proof.
- Genesis blocks for main/test/regtest.
- Message-start bytes and default ports.
- Address prefixes / Bech32 HRPs.
- DNS/fixed seeds.
- Difficulty and activation parameters.
- Assume-valid / chainwork values only after the chain exists.
- Test vectors and functional tests for every consensus change.

## 4. Repository target structure
- `src/` Bitcoin-derived node/wallet code after fork.
- `test/` upstream + Qitcoin functional tests.
- `contrib/` packaging, seeds, developer tooling.
- `doc/` protocol/build/operator docs.
- `qitcoin/` project-specific launch manifests and governance docs.

## 5. Public-facing services
- Node binaries: qitcoind, qitcoin-cli, qitcoin-qt.
- Testnet faucet.
- Block explorer (separate service; never consensus-critical).
- Status page / seed telemetry.
- Signed releases and checksums.

## 6. Release gates
- Build green on Linux/Windows/macOS.
- Unit + functional + integration tests green.
- IBD/reindex/pruning/wallet restore tested.
- Multi-node fork/reorg testing.
- Fuzzing and sanitizer runs.
- Reproducible-build process.
- External security review.
- Public testnet soak period.
- Mainnet genesis ceremony and signed release.
