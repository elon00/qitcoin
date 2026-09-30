# Qitcoin Coin Specification v0.1

| Parameter | Initial decision |
|---|---|
| Name | Qitcoin |
| Symbol | QTC |
| Max supply | 1,000,000,000,000 QTC |
| Decimals | 6 |
| Smallest unit | qit |
| Accounting maximum | 1,000,000,000,000,000,000 qits |
| Ledger | UTXO |
| Consensus | Proof of Work |
| PoW hash | SHA-256d (initial compatibility choice) |
| Signatures | Bitcoin-compatible baseline; PQC should be a separately specified future upgrade, not a silent consensus modification |
| Mainnet status | Disabled / not launched |

## Supply rule
The exact subsidy schedule must mathematically sum to no more than 1 trillion QTC. Do not approximate this with a conventional Bitcoin halving schedule and assume it reaches the requested cap. The implementation must include a consensus unit test that sums all subsidy eras and verifies the cap.

## Decimal rationale
`1,000,000,000,000 QTC * 1,000,000 qits/QTC = 1,000,000,000,000,000,000 qits` (1e18), which fits in signed 64-bit integer range.
