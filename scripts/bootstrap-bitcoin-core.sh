#!/usr/bin/env bash
set -euo pipefail
UPSTREAM_REF="${UPSTREAM_REF:-master}"
mkdir -p upstream
if [ ! -d upstream/bitcoin/.git ]; then
  git clone https://github.com/bitcoin/bitcoin.git upstream/bitcoin
fi
cd upstream/bitcoin
git fetch --tags origin
git checkout "$UPSTREAM_REF"
echo "Bitcoin Core source ready at upstream/bitcoin ($UPSTREAM_REF)."
echo "Next: pin a reviewed release tag, then implement the Qitcoin consensus patch set documented in docs/."
