#!/usr/bin/env python3
from pathlib import Path
import sys

required = [
    "README.md", "SECURITY.md", "docs/COIN_SPEC.md", "docs/ROADMAP.md",
    "docs/TEST_MATRIX.md", "docs/MAINNET_READINESS.md",
    "scripts/prepare_qitcoin_core.py", "tools/verify_supply.py",
    "tests/test_monetary_policy.py"
]
missing = [p for p in required if not Path(p).exists()]
if missing:
    print("MISSING:", *missing, sep="\n- ")
    sys.exit(1)

bad = []
for p in Path(".").rglob("*"):
    if p.is_file() and ".git" not in p.parts:
        try:
            t = p.read_text(errors="ignore")
        except Exception:
            continue
        # Fixed credentials are allowed only in isolated regtest fixtures.
        normalized = str(p).replace("\\", "/")
        test_fixture = normalized in {
            "docker/node1.conf", "docker/node2.conf", "docker/node3.conf",
            "test/functional/test_qitcoin_3nodes.py"
        }
        if "secure_qtc_password_2026" in t and p.name not in {".env.example", "readiness_check.py"} and not test_fixture:
            bad.append(str(p))
if bad:
    print("Hard-coded example credentials found outside .env.example:", bad)
    sys.exit(1)

print("Repository readiness checks passed.")
