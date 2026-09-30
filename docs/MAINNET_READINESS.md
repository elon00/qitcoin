# Qitcoin Mainnet Readiness Gates

Status legend: ✅ automated/complete in repo, 🟡 technically implementable by solo developer but not yet proven, 🔴 requires independent/external evidence.

## Consensus / Core
- ✅ 1 trillion QTC cap math with 6 decimals and int64 safety checks.
- ✅ Deterministic genesis values independently reproduced by tooling.
- ✅ Bitcoin Core upstream pinned to v30.2 for the Core-port workflow.
- ✅ Deterministic transformation script for monetary policy, genesis, ports and network identifiers.
- 🟡 C++ Core build must compile successfully in CI after transformation.
- 🟡 Native unit/functional tests must pass on the transformed Core tree.
- 🟡 Multi-node reorg, restart, reindex, prune and wallet recovery tests must pass.
- 🟡 Release binaries/checksums must be generated reproducibly.

## Network
- ✅ Unique main/test/reg P2P magic-byte plan and port plan.
- ✅ Bitcoin DNS/fixed seeds are removed by the transform for new-chain isolation.
- 🟡 At least 3 independent public testnet nodes.
- 🟡 Testnet faucet/explorer backed by the native Core node (not the Python simulator).
- 🟡 Public soak period with incident/upgrade procedure.

## Security
- ✅ Security policy and no-mainnet-with-mocks rule.
- 🟡 Fuzz/sanitizer runs on consensus/RPC/wallet surfaces.
- 🟡 RPC authentication and network exposure review.
- 🟡 PQC bridge must fail closed if real ML-DSA/ML-KEM implementation is absent.
- 🔴 Independent third-party security audit/sign-off.

## Operations / legal
- 🟡 Backup/restore, key rotation, monitoring, rollback and release runbooks.
- 🟡 Mainnet launch checklist with signed release hashes.
- 🔴 Jurisdiction-specific legal/regulatory review, exchange approvals, and independent node operators.

A Render web-service named “mainnet” does not satisfy these gates and must not be used as evidence of a live sovereign mainnet.
