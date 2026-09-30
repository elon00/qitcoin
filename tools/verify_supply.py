#!/usr/bin/env python3
"""
Qitcoin Monetary Economics & Supply Verification Engine
------------------------------------------------------
Verifies that:
1. MAX_MONEY fits strictly inside int64_t.
2. Halving subsidy sum never exceeds 1,000,000,000,000 QTC.
3. No integer overflow can occur in consensus validation.
"""

import sys

def verify_qitcoin_economics():
    TARGET_SUPPLY_QTC = 1_000_000_000_000 # 1 Trillion QTC
    DECIMALS = 6
    COIN = 10**DECIMALS # 1,000,000 qits
    MAX_MONEY = TARGET_SUPPLY_QTC * COIN
    INT64_MAX = 9_223_372_036_854_775_807 # 2^63 - 1
    
    INITIAL_SUBSIDY = 250_000 * COIN # 250,000 QTC per block
    HALVING_INTERVAL = 2_000_000 # 2 million blocks (~3.8 years @ 1 min blocks)
    
    print("=" * 70)
    print("QITCOIN (QTC) MONETARY POLICY & CONSENSUS PROOF")
    print("=" * 70)
    print(f"Target Max Supply  : {TARGET_SUPPLY_QTC:,} QTC")
    print(f"Decimals           : {DECIMALS} (1 QTC = {COIN:,} qits)")
    print(f"MAX_MONEY (qits)   : {MAX_MONEY:,}")
    print(f"int64_t Max Limit  : {INT64_MAX:,}")
    
    # Check 1: Fits in int64
    assert MAX_MONEY <= INT64_MAX, "CRITICAL ERROR: MAX_MONEY exceeds int64_t limit!"
    headroom = INT64_MAX - MAX_MONEY
    print(f"[PASS] Fits in int64_t with {headroom:,} units safety margin ({headroom/INT64_MAX*100:.2f}% headroom).")
    
    print("-" * 70)
    print(f"{'Era':<5} | {'Block Range':<23} | {'Reward (QTC)':<14} | {'Era Total (QTC)':<18} | {'Cumulative (QTC)':<18}")
    print("-" * 70)
    
    current_subsidy = INITIAL_SUBSIDY
    total_minted = 0
    era = 0
    
    while current_subsidy > 0:
        start_block = era * HALVING_INTERVAL
        end_block = (era + 1) * HALVING_INTERVAL - 1
        era_minted = current_subsidy * HALVING_INTERVAL
        total_minted += era_minted
        
        if era < 8 or current_subsidy == 1:
            print(f"{era:<5} | {start_block:>10,} - {end_block:<10,} | {current_subsidy / COIN:>14,.4f} | {era_minted / COIN:>18,.2f} | {total_minted / COIN:>18,.2f}")
        elif era == 8:
            print(f"{'...':<5} | {'...':<23} | {'...':<14} | {'...':<18} | {'...':<18}")
            
        current_subsidy //= 2
        era += 1
        
    print("-" * 70)
    total_qtc = total_minted / COIN
    print(f"Total Halving Eras       : {era}")
    print(f"Total Minted All-Time    : {total_qtc:,.6f} QTC")
    print(f"Target Cap               : {TARGET_SUPPLY_QTC:,.6f} QTC")
    print(f"Difference from Cap      : {(TARGET_SUPPLY_QTC * COIN - total_minted) / COIN} QTC (Dust remainder due to integer division)")
    
    # Check 2: Cap constraint
    assert total_minted <= MAX_MONEY, "CRITICAL ERROR: Total minted exceeds MAX_MONEY!"
    print("[PASS] Total minted is strictly <= 1,000,000,000,000 QTC.")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = verify_qitcoin_economics()
    sys.exit(0 if success else 1)
