#!/usr/bin/env bash
# Qitcoin Release Packaging Script (Linux / macOS)
set -e

VERSION="0.1.0-rc1"
DIST_DIR="dist"
ARCH="$(uname -m)"
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
PACKAGE_NAME="qitcoin-${VERSION}-${ARCH}-${OS}"

echo "=== Packaging Qitcoin Release ${VERSION} ==="
mkdir -p "${DIST_DIR}/${PACKAGE_NAME}/bin"
mkdir -p "${DIST_DIR}/${PACKAGE_NAME}/doc"

# Copy binaries if present
if [ -f "src/qitcoind" ]; then
    cp src/qitcoind src/qitcoin-cli "${DIST_DIR}/${PACKAGE_NAME}/bin/"
elif [ -f "upstream/bitcoin/src/qitcoind" ]; then
    cp upstream/bitcoin/src/qitcoind upstream/bitcoin/src/qitcoin-cli "${DIST_DIR}/${PACKAGE_NAME}/bin/"
fi

# Copy configurations and docs
cp -r docker/*.conf "${DIST_DIR}/${PACKAGE_NAME}/" 2>/dev/null || true
cp README.md LICENSE "${DIST_DIR}/${PACKAGE_NAME}/"
cp docs/*.md "${DIST_DIR}/${PACKAGE_NAME}/doc/"

# Create tarball
cd "${DIST_DIR}"
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}"
sha256sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.sha256"

echo "Release package created:"
echo "Archive: ${DIST_DIR}/${PACKAGE_NAME}.tar.gz"
cat "${PACKAGE_NAME}.tar.gz.sha256"
