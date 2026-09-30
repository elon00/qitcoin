#!/usr/bin/env python3
"""
Secure API Key & Secrets Manager for Qitcoin
--------------------------------------------
Safely loads, validates, and manages API keys and cross-chain credentials:
- Validates presence of AI keys (Gemini, OpenAI, Claude) without logging secret values.
- Masks keys for display (e.g. 'AIzaSy...abcd').
- Auto-generates local .env file if missing.
"""

import os
import re
from typing import Dict, Optional

class APIKeyManager:
    def __init__(self, env_path: str = ".env"):
        self.env_path = env_path
        self.keys = {}
        self.load_keys()

    def load_keys(self):
        """Load variables from .env file or system environment."""
        if os.path.exists(self.env_path):
            with open(self.env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        self.keys[k.strip()] = v.strip().strip('"').strip("'")
        
        # Override with OS environment variables if present
        for env_var in ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                        "ETHEREUM_RPC_URL", "SOLANA_RPC_URL", "BITCOIN_RPC_URL"]:
            if os.getenv(env_var):
                self.keys[env_var] = os.getenv(env_var)

    def get_key(self, key_name: str, default: Optional[str] = None) -> Optional[str]:
        return self.keys.get(key_name, default)

    def set_key(self, key_name: str, key_val: str):
        """Safely write/update key in local .env."""
        self.keys[key_name] = key_val
        lines = []
        key_found = False
        if os.path.exists(self.env_path):
            with open(self.env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{key_name}="):
                new_lines.append(f"{key_name}={key_val}\n")
                key_found = True
            else:
                new_lines.append(line)

        if not key_found:
            new_lines.append(f"{key_name}={key_val}\n")

        with open(self.env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    def get_masked_status(self) -> Dict[str, Dict[str, Any]]:
        """Return safe masked representation for UI inspection."""
        monitored_keys = [
            "GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
            "ETHEREUM_RPC_URL", "SOLANA_RPC_URL", "BRIDGE_RELAYER_PQC_SEED"
        ]
        status = {}
        for k in monitored_keys:
            val = self.keys.get(k, "")
            is_set = bool(val and not val.startswith("your_") and not val.startswith("AIzaSy...") and not val.startswith("sk-"))
            masked = f"{val[:6]}...{val[-4:]}" if len(val) > 10 else ("Configured" if is_set else "Not Set")
            status[k] = {
                "configured": is_set,
                "display": masked if is_set else "Missing (Add in Settings)"
            }
        return status

key_manager = APIKeyManager()

if __name__ == "__main__":
    print("API Key Manager Status:")
    for k, v in key_manager.get_masked_status().items():
        print(f"  {k}: {v['display']}")
