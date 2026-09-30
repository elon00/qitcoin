# Multichain Bridge & Cross-Chain Swap Masterplan

## 1. Executive Summary & The Question: "What is the Best Bridge Protocol?"

Cross-chain bridging is the single most attacked infrastructure in cryptocurrency history, responsible for over **\$2.8 Billion** in historical exploits (Ronin, Wormhole, Nomad, Harmony Horizon). 

When building a bridge for a **Bitcoin-family UTXO Layer-1 blockchain (like Qitcoin QTC)**, bridge protocols fall into three distinct classes:

| Bridge Architecture | Security Model | Trust Assumptions | UTXO / Non-EVM Compatibility | Best Use Case |
|---|---|---|---|---|
| **1. HTLC (Hashed Time-Locked Contracts)** | **Pure Cryptographic Math** (Zero Trusted Parties) | **Trustless**: Either both sides settle or both sides refund automatically via SHA-256 timelock. | **Native**: Supported out-of-the-box by Bitcoin/Qitcoin Script (`OP_CHECKLOCKTIMEVERIFY`). | **Direct Peer-to-Peer & DEX Swaps** |
| **2. TSS-MPC (Threshold Signature Scheme)** | **Multi-Party Computation** ($m$-of-$n$ Quorum) | **Federated Trust**: $m$ distributed validators must jointly sign vault transactions. | **Universal**: Works with any blockchain without modifying L1 consensus. | **Minting Wrapped Tokens (`wQTC`) on Ethereum, Solana, and Algorand** |
| **3. Chainlink CCIP / LayerZero v2** | **Decentralized Oracle + Verification Networks** | **Oracle Network**: Independent verification networks validate state. | **EVM/SVM Focused**: Requires smart contract capability on both sides or light clients. | **Smart Contract Ecosystem Messaging** |

### The Verdict: The "Best" Bridge Protocol for Qitcoin
**There is no single protocol that fits every need; the industry-leading approach is a Defense-in-Depth Hybrid Architecture:**

1. **For Trustless Trading (QTC $\leftrightarrow$ BTC, ETH, SOL)**: **HTLC Atomic Swaps** are the absolute best protocol because **funds can never be hacked or stolen by a third party**. If an exchange fails, user funds automatically return after the timelock expires.
2. **For High-Speed Cross-Chain Liquidity (`wQTC`)**: **TSS-MPC Federation protected by NIST FIPS 204 (ML-DSA) Post-Quantum Signatures** with:
   * **Proof-of-Reserve Real-Time Attestation** (Total locked QTC $\ge$ Total minted wQTC).
   * **Velocity Rate Limiting** (Max 5,000,000 QTC transfer per hour).
   * **Autonomous Circuit Breaker** (Halts bridge automatically if abnormal volume or reorg detected).

---

## 2. Technical Bridge Architecture

```
+-----------------------------------------------------------------------------------+
|                           QITCOIN MULTICHAIN BRIDGE                               |
+-----------------------------------------------------------------------------------+
                                       |
           +---------------------------+---------------------------+
           |                                                       |
           v                                                       v
   [TIER 1: TRUSTLESS SWAP]                                [TIER 2: LIQUIDITY BRIDGE]
   HTLC Atomic Swap Protocol                               TSS-MPC wQTC Vault System
   * Direct QTC <-> BTC / ETH / SOL                        * Mint wQTC on EVM / Solana / Algorand
   * Script: OP_SHA256 & CLTV                              * NIST FIPS 204 Post-Quantum Attestation
   * Zero Custodial Risk                                   * Proof-of-Reserve Real-Time Verifier
   * Auto-Refund on Expiry                                 * Emergency Circuit Breaker
```

---

## 3. HTLC Script Specification on Qitcoin L1

In standard Bitcoin/Qitcoin Script:
```
OP_IF
    OP_SHA256 <SecretHash_32Bytes> OP_EQUALVERIFY
    <RecipientPubKey> OP_CHECKSIG
OP_ELSE
    <Locktime_BlockHeight_Or_UnixTime> OP_CHECKLOCKTIMEVERIFY OP_DROP
    <SenderPubKey> OP_CHECKSIG
OP_ENDIF
```

* **Step 1 (Alice creates Secret)**: Alice generates random secret $S$ (32 bytes) and computes $H = \text{SHA256}(S)$.
* **Step 2 (Deposit on QTC)**: Alice locks 100,000 QTC in HTLC script with hash $H$ and 2-hour timelock for Bob.
* **Step 3 (Deposit on Counterparty Chain)**: Bob locks 0.15 BTC or 5,000 USDT on Ethereum with the same hash $H$ and 1-hour timelock for Alice.
* **Step 4 (Alice Claims Counterparty)**: Alice submits $S$ to claim Bob's deposit. $S$ is now publicly revealed on-chain!
* **Step 5 (Bob Claims QTC)**: Bob reads $S$ from Alice's claim transaction and uses $S$ to claim Alice's 100,000 QTC.
* **Failure Safety**: If Bob refuses or goes offline, Alice recovers all 100,000 QTC after the 2-hour timelock.

---

## 4. NIST Post-Quantum Cryptography (PQC) Security Layer

Standard bridges rely on ECDSA (secp256k1) or Ed25519 signatures. A future quantum computer executing Shor's algorithm can derive the private key from public keys and forge bridge attestations.

Qitcoin's bridge solves this by applying **NIST FIPS 204 (ML-DSA-65)**:
* Bridge relayer attestations are signed using lattice-based digital signatures ($q = 8,380,417, n = 256$).
* Signature length: 3,309 bytes.
* Provides **NIST Category 3 (128-bit quantum security)**.
* Even if ECDSA is broken in 2030+, Qitcoin bridge vaults remain secure against quantum decryption.

---

## 5. Security Guardrails & Emergency Controls

1. **Proof-of-Reserve Real-time Tracker**:
   * Nodes constantly verify: $\text{Reserve Ratio} = \frac{\text{Locked Native QTC}}{\sum \text{Minted wQTC}} \ge 100\%$.
2. **Velocity Rate Limiter**:
   * Single transaction cap: 5,000,000 QTC.
   * Hourly aggregate cap: 15,000,000 QTC.
3. **Autonomous Circuit Breaker**:
   * If an unverified minting event occurs on Ethereum/Solana without a matching Qitcoin block confirmation, the bridge relayer automatically halts withdrawals and raises an alert.
