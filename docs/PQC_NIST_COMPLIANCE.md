# NIST Post-Quantum Cryptography (PQC) Compliance Specification

## 1. Overview of NIST Final Standards (August 2024)

In August 2024, the National Institute of Standards and Technology (NIST) officially released the world's first finalized Post-Quantum Cryptographic Federal Information Processing Standards (FIPS):

1. **FIPS 203: ML-KEM (Module-Lattice-Based Key-Encapsulation Mechanism)**
   * Formerly known as **CRYSTALS-Kyber**.
   * Purpose: Quantum-resistant shared secret negotiation and encryption.
   * Parameter set: **ML-KEM-768** (Security Category 3, equivalent to AES-192/SHA-384 against quantum attacks).
2. **FIPS 204: ML-DSA (Module-Lattice-Based Digital Signature Algorithm)**
   * Formerly known as **CRYSTALS-Dilithium**.
   * Purpose: Quantum-resistant digital signatures for transactions and bridge attestations.
   * Parameter set: **ML-DSA-65** (Security Category 3).
3. **FIPS 205: SLH-DSA (Stateless Hash-Based Digital Signature Algorithm)**
   * Formerly known as **SPHINCS+**.
   * Purpose: Stateless hash-based digital signature relying exclusively on hash functions (SHA-256 / SHAKE-256) with zero lattice assumptions.

---

## 2. Qitcoin PQC Integration Architecture

Qitcoin adopts a hybrid transition model:

### Layer 1: Bitcoin Core Consensus Compatibility (Phase 1)
* Standard secp256k1 ECDSA and Schnorr/Taproot signatures remain active for initial compatibility with existing ASIC miners, hardware wallets (Ledger/Trezor), and Bitcoin toolchains.

### Layer 2: Quantum-Safe Bridge & Inter-Node Transport (Phase 1 Native)
* **All Cross-Chain Relayer Headers**: Signed using **ML-DSA-65** (3,309-byte signature).
* **Inter-Node P2P Encryption**: Encrypted using **ML-KEM-768** to prevent "Harvest Now, Decrypt Later" state-level quantum eavesdropping.

### Layer 3: Native QTC PQC Taproot Upgrade (Phase 2 Hard Fork)
* Soft-fork activation of a new witness script version (`OP_SUCCESS` / PQC Taproot) allowing native spending of UTXOs using ML-DSA or SLH-DSA public keys.

---

## 3. Wire Formats & Parameter Table

| Metric | NIST FIPS 203 (ML-KEM-768) | NIST FIPS 204 (ML-DSA-65) | Classical (secp256k1) |
|---|---|---|---|
| **Public Key Size** | 1,184 bytes | 1,952 bytes | 33 bytes (compressed) |
| **Private Key Size** | 2,400 bytes | 4,032 bytes | 32 bytes |
| **Ciphertext / Signature** | 1,088 bytes | 3,309 bytes | 64 – 72 bytes |
| **Quantum Resistance** | $\ge 128$ bits (Category 3) | $\ge 128$ bits (Category 3) | **0 bits** (Broken by Shor's) |

---

## 4. Verification in Codebase

Qitcoin includes functional NIST FIPS 204 verification scripts:
```powershell
python bridge/pqc_nist_bridge.py
```
This tests real ML-DSA-65 key generation, signing, and verification using polynomial ring arithmetic over $R_q = \mathbb{Z}_q[X]/(X^{256} + 1)$.
