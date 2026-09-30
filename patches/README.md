# Consensus Patch Queue

The following verified consensus patches are implemented in this repository:

1. `01_amount_and_maxmoney.patch` - Sets 6 decimals (`COIN = 1,000,000 qits`) and `MAX_MONEY = 1,000,000,000,000 QTC` (10^18 qits). Prevents int64_t overflow.
2. `02_subsidy_and_halving.patch` - Implements the 250,000 QTC initial block reward, 2,000,000 blocks halving interval (~3.8 yrs at 1 min blocks), strictly capping total coins to 999,999,999,974 QTC.
3. `03_chainparams_and_network.patch` - Configures QTC P2P/RPC ports (`19333`/`19332`), magic bytes `0x71746301`, 1-minute block time (`nPowTargetSpacing = 60`), and address prefixes (`Q` for P2PKH, `T` for P2SH, `qtc` for Bech32).
4. `04_genesis_block.patch` - Hardcodes the mined Genesis block hashes, nonces, and Merkle root with the unique timestamp phrase *"The Times 30/Sep/2026 Qitcoin: The Decentralized Trillion Economy"*.

