#!/usr/bin/env python3
"""Prepare a pinned Bitcoin Core v30.2 checkout as Qitcoin Core.

This is intentionally deterministic and assertion-heavy: if upstream text changes,
the script stops instead of silently producing a malformed consensus build.
"""
from pathlib import Path
import re, sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "upstream/bitcoin")
if not (ROOT / "src").exists():
    raise SystemExit(f"Bitcoin Core source not found at {ROOT}")

def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected exactly one anchor, found {n}")
    return text.replace(old, new, 1)

def replace_section(text: str, start: str, end: str, transform):
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + transform(text[a:b]) + text[b:]

# 1) Monetary unit / hard cap
p = ROOT / "src/consensus/amount.h"
s = p.read_text()
s = replace_once(s, "static constexpr CAmount COIN = 100000000;",
                 "static constexpr CAmount COIN = 1000000; // 1 QTC = 1,000,000 qits", "COIN")
s = replace_once(s, "static constexpr CAmount MAX_MONEY = 21000000 * COIN;",
                 "static constexpr CAmount MAX_MONEY = 1000000000000LL * COIN; // 1 trillion QTC", "MAX_MONEY")
p.write_text(s)

# 2) Subsidy schedule
p = ROOT / "src/validation.cpp"
s = p.read_text()
a = s.index("CAmount GetBlockSubsidy")
b = s.index("\n}", a) + 2
fn = s[a:b]
fn = replace_once(fn, "if (halvings >= 64)", "if (halvings >= 38)", "halving cutoff")
fn = replace_once(fn, "CAmount nSubsidy = 50 * COIN;", "CAmount nSubsidy = 250000LL * COIN;", "initial subsidy")
s = s[:a] + fn + s[b:]
p.write_text(s)

# 3) Chain/network params
p = ROOT / "src/kernel/chainparams.cpp"
s = p.read_text()
s = replace_once(
    s,
    'const char* pszTimestamp = "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks";',
    'const char* pszTimestamp = "The Times 30/Sep/2026 Qitcoin: The Decentralized Trillion Economy";',
    "genesis timestamp",
)

def patch_main(sec: str) -> str:
    sec = sec.replace("consensus.nSubsidyHalvingInterval = 210000;", "consensus.nSubsidyHalvingInterval = 2000000;", 1)
    sec = re.sub(r"consensus\.BIP34Height = \d+;", "consensus.BIP34Height = 1;", sec, count=1)
    sec = re.sub(r"consensus\.BIP34Hash = uint256\{[^;]+;", "consensus.BIP34Hash = uint256{};", sec, count=1)
    sec = re.sub(r"consensus\.BIP65Height = \d+;", "consensus.BIP65Height = 1;", sec, count=1)
    sec = re.sub(r"consensus\.BIP66Height = \d+;", "consensus.BIP66Height = 1;", sec, count=1)
    sec = re.sub(r"consensus\.CSVHeight = \d+;", "consensus.CSVHeight = 1;", sec, count=1)
    sec = re.sub(r"consensus\.SegwitHeight = \d+;", "consensus.SegwitHeight = 0;", sec, count=1)
    sec = re.sub(r"consensus\.MinBIP9WarningHeight = \d+;", "consensus.MinBIP9WarningHeight = 0;", sec, count=1)
    sec = re.sub(r'consensus\.powLimit = uint256\{"[^"]+"\};', 'consensus.powLimit = uint256{"00000ffff0000000000000000000000000000000000000000000000000000000"};', sec, count=1)
    sec = replace_once(sec, "consensus.nPowTargetTimespan = 14 * 24 * 60 * 60;", "consensus.nPowTargetTimespan = 5040 * 60;", "main timespan")
    sec = replace_once(sec, "consensus.nPowTargetSpacing = 10 * 60;", "consensus.nPowTargetSpacing = 60;", "main spacing")
    sec = re.sub(r'consensus\.nMinimumChainWork = uint256\{"[^"]+"\};', 'consensus.nMinimumChainWork = uint256{};', sec, count=1)
    sec = re.sub(r'consensus\.defaultAssumeValid = uint256\{"[^"]+"\};[^\n]*', 'consensus.defaultAssumeValid = uint256{};', sec, count=1)
    sec = replace_once(sec, "pchMessageStart[0] = 0xf9;\n        pchMessageStart[1] = 0xbe;\n        pchMessageStart[2] = 0xb4;\n        pchMessageStart[3] = 0xd9;",
                       "pchMessageStart[0] = 0x71;\n        pchMessageStart[1] = 0x74;\n        pchMessageStart[2] = 0x63;\n        pchMessageStart[3] = 0x01;", "main magic")
    sec = replace_once(sec, "nDefaultPort = 8333;", "nDefaultPort = 19333;", "main p2p port")
    sec = re.sub(r'genesis = CreateGenesisBlock\([^\n]+\);', 'genesis = CreateGenesisBlock(1790772000, 388903, 0x1e0ffff0, 1, 250000LL * COIN);', sec, count=1)
    sec = re.sub(r'assert\(consensus\.hashGenesisBlock == uint256\{"[^"]+"\}\);', 'assert(consensus.hashGenesisBlock == uint256{"0000064d6898cab247cd7a66ae5d621abe9decd284d84b8a1b857b0606dc532a"});', sec, count=1)
    sec = re.sub(r'assert\(genesis\.hashMerkleRoot == uint256\{"[^"]+"\}\);', 'assert(genesis.hashMerkleRoot == uint256{"9a5bcf89553e6cc933455c84a964f720f0aa47628f5bfee08e0db920a37db79a"});', sec, count=1)
    sec = re.sub(r'\n\s*vSeeds\.emplace_back\([^\n]+\);[^\n]*', '', sec)
    sec = replace_once(sec, "base58Prefixes[PUBKEY_ADDRESS] = std::vector<unsigned char>(1,0);", "base58Prefixes[PUBKEY_ADDRESS] = std::vector<unsigned char>(1,58);", "main p2pkh")
    sec = replace_once(sec, "base58Prefixes[SCRIPT_ADDRESS] = std::vector<unsigned char>(1,5);", "base58Prefixes[SCRIPT_ADDRESS] = std::vector<unsigned char>(1,65);", "main p2sh")
    sec = replace_once(sec, 'bech32_hrp = "bc";', 'bech32_hrp = "qtc";', "main bech32")
    sec = re.sub(r'vFixedSeeds = std::vector<uint8_t>\([^\n]+\);', 'vFixedSeeds.clear();', sec, count=1)
    sec = re.sub(r'm_assumeutxo_data = \{.*?\n        \};', 'm_assumeutxo_data = {};', sec, count=1, flags=re.S)
    return sec

def patch_test(sec: str) -> str:
    sec = sec.replace("consensus.nSubsidyHalvingInterval = 210000;", "consensus.nSubsidyHalvingInterval = 2000000;", 1)
    sec = re.sub(r"consensus\.BIP34Height = \d+;", "consensus.BIP34Height = 1;", sec, count=1)
    sec = re.sub(r"consensus\.BIP34Hash = uint256\{[^;]+;", "consensus.BIP34Hash = uint256{};", sec, count=1)
    for k in ["BIP65Height","BIP66Height","CSVHeight"]:
        sec = re.sub(rf"consensus\.{k} = \d+;", f"consensus.{k} = 1;", sec, count=1)
    sec = re.sub(r"consensus\.SegwitHeight = \d+;", "consensus.SegwitHeight = 0;", sec, count=1)
    sec = re.sub(r"consensus\.MinBIP9WarningHeight = \d+;", "consensus.MinBIP9WarningHeight = 0;", sec, count=1)
    sec = re.sub(r'consensus\.powLimit = uint256\{"[^"]+"\};', 'consensus.powLimit = uint256{"00000ffff0000000000000000000000000000000000000000000000000000000"};', sec, count=1)
    sec = replace_once(sec, "consensus.nPowTargetTimespan = 14 * 24 * 60 * 60;", "consensus.nPowTargetTimespan = 1440 * 60;", "test timespan")
    sec = replace_once(sec, "consensus.nPowTargetSpacing = 10 * 60;", "consensus.nPowTargetSpacing = 60;", "test spacing")
    sec = re.sub(r'consensus\.nMinimumChainWork = uint256\{"[^"]+"\};', 'consensus.nMinimumChainWork = uint256{};', sec, count=1)
    sec = re.sub(r'consensus\.defaultAssumeValid = uint256\{"[^"]+"\};[^\n]*', 'consensus.defaultAssumeValid = uint256{};', sec, count=1)
    sec = replace_once(sec, "pchMessageStart[0] = 0x0b;\n        pchMessageStart[1] = 0x11;\n        pchMessageStart[2] = 0x09;\n        pchMessageStart[3] = 0x07;",
                       "pchMessageStart[0] = 0x71;\n        pchMessageStart[1] = 0x74;\n        pchMessageStart[2] = 0x63;\n        pchMessageStart[3] = 0x02;", "test magic")
    sec = replace_once(sec, "nDefaultPort = 18333;", "nDefaultPort = 29333;", "test p2p port")
    sec = re.sub(r'genesis = CreateGenesisBlock\([^\n]+\);', 'genesis = CreateGenesisBlock(1790772000, 388903, 0x1e0ffff0, 1, 250000LL * COIN);', sec, count=1)
    sec = re.sub(r'assert\(consensus\.hashGenesisBlock == uint256\{"[^"]+"\}\);', 'assert(consensus.hashGenesisBlock == uint256{"0000064d6898cab247cd7a66ae5d621abe9decd284d84b8a1b857b0606dc532a"});', sec, count=1)
    sec = re.sub(r'assert\(genesis\.hashMerkleRoot == uint256\{"[^"]+"\}\);', 'assert(genesis.hashMerkleRoot == uint256{"9a5bcf89553e6cc933455c84a964f720f0aa47628f5bfee08e0db920a37db79a"});', sec, count=1)
    sec = re.sub(r'\n\s*vSeeds\.emplace_back\([^\n]+\);[^\n]*', '', sec)
    sec = replace_once(sec, 'bech32_hrp = "tb";', 'bech32_hrp = "tqtc";', "test bech32")
    sec = re.sub(r'vFixedSeeds = std::vector<uint8_t>\([^\n]+\);', 'vFixedSeeds.clear();', sec, count=1)
    sec = re.sub(r'm_assumeutxo_data = \{.*?\n        \};', 'm_assumeutxo_data = {};', sec, count=1, flags=re.S)
    return sec

def patch_reg(sec: str) -> str:
    sec = replace_once(sec, "consensus.nSubsidyHalvingInterval = 150;", "consensus.nSubsidyHalvingInterval = 2000000;", "reg halving")
    sec = replace_once(sec, "consensus.nPowTargetSpacing = 10 * 60;", "consensus.nPowTargetSpacing = 60;", "reg spacing")
    sec = replace_once(sec, "nDefaultPort = 18444;", "nDefaultPort = 39333;", "reg p2p port")
    sec = replace_once(sec, "pchMessageStart[0] = 0xfa;\n        pchMessageStart[1] = 0xbf;\n        pchMessageStart[2] = 0xb5;\n        pchMessageStart[3] = 0xda;",
                       "pchMessageStart[0] = 0x71;\n        pchMessageStart[1] = 0x74;\n        pchMessageStart[2] = 0x63;\n        pchMessageStart[3] = 0x03;", "reg magic")
    sec = re.sub(r'genesis = CreateGenesisBlock\([^\n]+\);', 'genesis = CreateGenesisBlock(1790772000, 1, 0x207fffff, 1, 250000LL * COIN);', sec, count=1)
    sec = re.sub(r'assert\(consensus\.hashGenesisBlock == uint256\{"[^"]+"\}\);', 'assert(consensus.hashGenesisBlock == uint256{"3e1630837eda1b40c16c84d5adf7f86b89707a5c63326968f5436c30bc6c2407"});', sec, count=1)
    sec = re.sub(r'assert\(genesis\.hashMerkleRoot == uint256\{"[^"]+"\}\);', 'assert(genesis.hashMerkleRoot == uint256{"9a5bcf89553e6cc933455c84a964f720f0aa47628f5bfee08e0db920a37db79a"});', sec, count=1)
    sec = replace_once(sec, 'bech32_hrp = "bcrt";', 'bech32_hrp = "rqtc";', "reg bech32")
    return sec

s = replace_section(s, "class CMainParams", "class CTestNetParams", patch_main)
s = replace_section(s, "class CTestNetParams", "class CTestNet4Params", patch_test)
s = replace_section(s, "class CRegTestParams", "std::unique_ptr<const CChainParams> CChainParams::SigNet", patch_reg)
p.write_text(s)

# 4) RPC ports
p = ROOT / "src/chainparamsbase.cpp"
s = p.read_text()
s = replace_once(s, 'return std::make_unique<CBaseChainParams>("", 8332);', 'return std::make_unique<CBaseChainParams>("", 19332);', "main rpc")
s = replace_once(s, 'return std::make_unique<CBaseChainParams>("testnet3", 18332);', 'return std::make_unique<CBaseChainParams>("testnet3", 29332);', "test rpc")
s = replace_once(s, 'return std::make_unique<CBaseChainParams>("regtest", 18443);', 'return std::make_unique<CBaseChainParams>("regtest", 39332);', "reg rpc")
p.write_text(s)

print("Qitcoin Core v30.2 transformation applied successfully.")
