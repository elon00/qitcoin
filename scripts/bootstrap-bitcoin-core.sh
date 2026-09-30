#!/usr/bin/env bash
set -euo pipefail
UPSTREAM_REF="${UPSTREAM_REF:-v30.2}"
mkdir -p upstream
if [ ! -d upstream/bitcoin/.git ]; then
  git clone https://github.com/bitcoin/bitcoin.git upstream/bitcoin
fi
cd upstream/bitcoin
git fetch --tags origin
git checkout "$UPSTREAM_REF"
echo "Bitcoin Core source ready at upstream/bitcoin ($UPSTREAM_REF)."
python ../../scripts/prepare_qitcoin_core.py .\necho "Qitcoin transformation applied to pinned Bitcoin Core $UPSTREAM_REF."
