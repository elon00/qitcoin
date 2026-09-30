#!/usr/bin/env python3
"""
Qitcoin Genesis Block Miner & Chainparams Generator
--------------------------------------------------
Constructs and mines valid Genesis blocks for Qitcoin:
- Mainnet
- Testnet
- Regtest

Outputs exact C++ parameters for `src/chainparams.cpp`.
"""

import hashlib
import struct
import time
import binascii

def sha256d(data: bytes) -> bytes:
    """Double SHA-256 hash."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def compact_to_target(n_bits: int) -> int:
    """Convert Bitcoin compact target format (nBits) to full uint256 target."""
    n_size = n_bits >> 24
    n_word = n_bits & 0x007fffff
    if n_size <= 3:
        target = n_word >> (8 * (3 - n_size))
    else:
        target = n_word << (8 * (n_size - 3))
    return target

def create_coinbase_tx(psz_timestamp: str, pubkey_hex: str, reward_qits: int) -> bytes:
    """Create raw serialized coinbase transaction."""
    # Version (4 bytes, little-endian)
    tx = struct.pack("<I", 1)
    
    # Vin count = 1
    tx += b"\x01"
    
    # Previous output hash (32 bytes 0x00)
    tx += b"\x00" * 32
    # Previous output index (0xffffffff)
    tx += struct.pack("<I", 0xffffffff)
    
    # ScriptSig: compact nBits + timestamp
    # 0x04, 0xffffff00 (dummy nbits push) + len + timestamp
    timestamp_bytes = psz_timestamp.encode("utf-8")
    script_sig = b"\x04\xff\xff\x00\x1d\x01\x04" + bytes([len(timestamp_bytes)]) + timestamp_bytes
    
    # ScriptSig length varint
    tx += bytes([len(script_sig)])
    tx += script_sig
    
    # Sequence (0xffffffff)
    tx += struct.pack("<I", 0xffffffff)
    
    # Vout count = 1
    tx += b"\x01"
    
    # Value (8 bytes, little-endian signed 64-bit int)
    tx += struct.pack("<q", reward_qits)
    
    # ScriptPubKey: push pubkey + OP_CHECKSIG
    pubkey_bytes = binascii.unhexlify(pubkey_key)
    script_pubkey = bytes([len(pubkey_bytes)]) + pubkey_bytes + b"\xac" # OP_CHECKSIG
    
    # ScriptPubKey length
    tx += bytes([len(script_pubkey)])
    tx += script_pubkey
    
    # Locktime (4 bytes, 0)
    tx += struct.pack("<I", 0)
    
    return tx

def mine_genesis_block(network_name: str, psz_timestamp: str, n_time: int, n_bits: int, reward_qits: int, pubkey_hex: str):
    print(f"=== Mining Genesis Block for Qitcoin [{network_name}] ===")
    print(f"Timestamp phrase: \"{psz_timestamp}\"")
    print(f"Unix Time: {n_time}")
    print(f"nBits: 0x{n_bits:08x}")
    print(f"Reward: {reward_qits / 1_000_000:,.2f} QTC ({reward_qits} qits)")
    
    target = compact_to_target(n_bits)
    tx = create_coinbase_tx(psz_timestamp, pubkey_hex, reward_qits)
    merkle_root = sha256d(tx)
    
    merkle_root_hex = merkle_root[::-1].hex()
    print(f"Merkle Root: {merkle_root_hex}")
    
    # Block header:
    # version (4 bytes, 1)
    # prev_block (32 bytes 0)
    # merkle_root (32 bytes)
    # n_time (4 bytes)
    # n_bits (4 bytes)
    # nonce (4 bytes)
    
    header_prefix = struct.pack("<I", 1) + (b"\x00" * 32) + merkle_root + struct.pack("<I", n_time) + struct.pack("<I", n_bits)
    
    nonce = 0
    start_time = time.time()
    last_print = start_time
    
    while True:
        header = header_prefix + struct.pack("<I", nonce)
        block_hash = sha256d(header)
        hash_int = int.from_bytes(block_hash, byteorder="little")
        
        if hash_int <= target:
            elapsed = time.time() - start_time
            hash_hex = block_hash[::-1].hex()
            print(f"\nSUCCESS! Found Genesis Block for {network_name} in {elapsed:.2f}s!")
            print(f"Nonce: {nonce}")
            print(f"Genesis Hash: {hash_hex}")
            print(f"Genesis Merkle: {merkle_root_hex}")
            return {
                "network": network_name,
                "nTime": n_time,
                "nNonce": nonce,
                "nBits": hex(n_bits),
                "hash": hash_hex,
                "merkle": merkle_root_hex,
                "timestamp": psz_timestamp
            }
            
        nonce += 1
        if nonce % 200000 == 0:
            now = time.time()
            if now - last_print > 2.0:
                hps = nonce / (now - start_time)
                print(f"Testing... Nonce: {nonce:,} | Hashrate: {hps:,.0f} H/s", end="\r")
                last_print = now

pubkey_key = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"

if __name__ == "__main__":
    timestamp_msg = "The Times 30/Sep/2026 Qitcoin: The Decentralized Trillion Economy"
    genesis_time = 1790772000 # 2026-09-30 12:40:00 UTC
    initial_reward = 250_000 * 1_000_000 # 250,000 QTC in qits
    
    # 1. Regtest (Very easy difficulty for instant dev: 0x207fffff)
    regtest = mine_genesis_block("Regtest", timestamp_msg, genesis_time, 0x207fffff, initial_reward, pubkey_key)
    
    # 2. Testnet / Mainnet (Light initial target for genesis: 0x1e0ffff0)
    testnet = mine_genesis_block("Testnet", timestamp_msg, genesis_time, 0x1e0ffff0, initial_reward, pubkey_key)
    mainnet = mine_genesis_block("Mainnet", timestamp_msg, genesis_time, 0x1e0ffff0, initial_reward, pubkey_key)
    
    print("\n" + "="*50)
    print("C++ CHAINPARAMS SNIPPET:")
    print("="*50)
    print(f"""
// Qitcoin Genesis Block Configuration
const char* pszTimestamp = "{timestamp_msg}";
const CScript genesisOutputScript = CScript() << ParseHex("{pubkey_key}") << OP_CHECKSIG;

// Mainnet:
// Hash:   uint256S("0x{mainnet['hash']}");
// Merkle: uint256S("0x{mainnet['merkle']}");
// CreateGenesisBlock({mainnet['nTime']}, {mainnet['nNonce']}, {mainnet['nBits']}, 1, 250000 * COIN);

// Testnet:
// Hash:   uint256S("0x{testnet['hash']}");
// Merkle: uint256S("0x{testnet['merkle']}");
// CreateGenesisBlock({testnet['nTime']}, {testnet['nNonce']}, {testnet['nBits']}, 1, 250000 * COIN);

// Regtest:
// Hash:   uint256S("0x{regtest['hash']}");
// Merkle: uint256S("0x{regtest['merkle']}");
// CreateGenesisBlock({regtest['nTime']}, {regtest['nNonce']}, {regtest['nBits']}, 1, 250000 * COIN);
""")
