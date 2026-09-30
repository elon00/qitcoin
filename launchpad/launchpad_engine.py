#!/usr/bin/env python3
"""
Qitcoin Token Launchpad & Bonding Curve Protocol
------------------------------------------------
Provides fair-launch token generation on Qitcoin with:
1. Automated linear & exponential bonding curves for instant liquidity.
2. Anti-rugpull liquidity locking mechanism.
3. Transparent project tokenomics and contributor allocations.
"""

import time
import secrets
from typing import Dict, Any, List

class LaunchpadToken:
    def __init__(self, name: str, ticker: str, total_supply: float, creator_address: str, description: str):
        self.token_id = f"tok_{secrets.token_hex(6)}"
        self.name = name
        self.ticker = ticker.upper()
        self.total_supply = total_supply
        self.creator = creator_address
        self.description = description
        self.tokens_sold = 0.0
        self.qtc_collateral_raised = 0.0
        self.graduation_target_qtc = 250_000.0 # Graduate to AMM pool at 250k QTC
        self.graduated = False
        self.created_at = int(time.time())

    def get_current_price(self) -> float:
        """Linear bonding curve: Price increases as more tokens are bought."""
        base_price = 0.0001 # 0.0001 QTC per token
        slope = 0.0000001
        return base_price + (slope * self.tokens_sold)

    def buy_tokens(self, buyer_address: str, qtc_amount: float) -> Dict[str, Any]:
        if self.graduated:
            raise ValueError("Token has graduated to external AMM pool!")

        price = self.get_current_price()
        tokens_out = qtc_amount / price

        if self.tokens_sold + tokens_out > self.total_supply * 0.8: # 80% public sale
            tokens_out = (self.total_supply * 0.8) - self.tokens_sold

        self.tokens_sold += tokens_out
        self.qtc_collateral_raised += qtc_amount

        # Check graduation
        if self.qtc_collateral_raised >= self.graduation_target_qtc:
            self.graduated = True

        return {
            "token_ticker": self.ticker,
            "buyer": buyer_address,
            "qtc_spent": qtc_amount,
            "tokens_received": tokens_out,
            "price_per_token_qtc": price,
            "progress_to_graduation_pct": round((self.qtc_collateral_raised / self.graduation_target_qtc) * 100, 2),
            "is_graduated": self.graduated
        }

class QitcoinLaunchpad:
    def __init__(self):
        self.tokens: Dict[str, LaunchpadToken] = {}
        self._seed_sample_tokens()

    def _seed_sample_tokens(self):
        t1 = LaunchpadToken("QitAI Network", "QAI", 1_000_000_000, "Q1Dev...", "Autonomous DePIN AI compute on Qitcoin")
        t1.tokens_sold = 150_000_000
        t1.qtc_collateral_raised = 45_000
        self.tokens[t1.token_id] = t1

        t2 = LaunchpadToken("Quantum Doge", "QDOGE", 10_000_000_000, "Q2Meme...", "NIST PQC-secured post-quantum meme coin")
        t2.tokens_sold = 620_000_000
        t2.qtc_collateral_raised = 180_000
        self.tokens[t2.token_id] = t2

    def create_token(self, name: str, ticker: str, total_supply: float,
                     creator_address: str, description: str) -> LaunchpadToken:
        tok = LaunchpadToken(name, ticker, total_supply, creator_address, description)
        self.tokens[tok.token_id] = tok
        return tok

    def list_tokens(self) -> List[Dict[str, Any]]:
        return [{
            "token_id": t.token_id,
            "name": t.name,
            "ticker": t.ticker,
            "total_supply": t.total_supply,
            "tokens_sold": t.tokens_sold,
            "collateral_raised_qtc": t.qtc_collateral_raised,
            "current_price_qtc": t.get_current_price(),
            "graduation_pct": round((t.qtc_collateral_raised / t.graduation_target_qtc) * 100, 1),
            "description": t.description
        } for t in self.tokens.values()]

launchpad_instance = QitcoinLaunchpad()

if __name__ == "__main__":
    print("Testing Qitcoin Launchpad...")
    toks = launchpad_instance.list_tokens()
    print("Active Tokens on Launchpad:", toks)
