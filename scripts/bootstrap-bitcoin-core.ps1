$ErrorActionPreference = "Stop"
$ref = if ($env:UPSTREAM_REF) { $env:UPSTREAM_REF } else { "v30.2" }
New-Item -ItemType Directory -Force -Path "upstream" | Out-Null
if (-not (Test-Path "upstream/bitcoin/.git")) {
  git clone https://github.com/bitcoin/bitcoin.git upstream/bitcoin
}
Push-Location upstream/bitcoin
git fetch --tags origin
git checkout $ref
Pop-Location
Write-Host "Bitcoin Core source ready at upstream/bitcoin ($ref)."
python ..\\..\\scripts\\prepare_qitcoin_core.py .\nWrite-Host "Qitcoin transformation applied to pinned Bitcoin Core $ref."
