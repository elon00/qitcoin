# Security Policy

## Supported scope
Security reports are accepted for Qitcoin Core consensus tooling, the testnet-alpha portal/API, wallet/RPC logic, bridge/x402 modules, and release automation.

## Mainnet safety rule
No release may be described as production mainnet-ready until all mandatory gates in `docs/MAINNET_READINESS.md` pass. Testnet-alpha is experimental and must not custody real-value funds.

## Secret handling
Never commit private keys, mnemonics, RPC passwords, cloud credentials, bridge relayer seeds, or exchange API keys. Use environment variables / secret stores only. Rotate any credential that has ever been committed.

## Vulnerability reporting
For now, use a private GitHub security advisory for this repository rather than opening a public issue for exploitable vulnerabilities.

## Cryptography
Mock/fallback cryptography must never be treated as production cryptography. Any PQC feature must fail closed when the real implementation is unavailable before mainnet.
