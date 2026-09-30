$ErrorActionPreference = "Stop"
$ref = if ($env:UPSTREAM_REF) { $env:UPSTREAM_REF } else { "master" }
New-Item -ItemType Directory -Force -Path "upstream" | Out-Null
if (-not (Test-Path "upstream/bitcoin/.git")) {
  git clone https://github.com/bitcoin/bitcoin.git upstream/bitcoin
}
Push-Location upstream/bitcoin
git fetch --tags origin
git checkout $ref
Pop-Location
Write-Host "Bitcoin Core source ready at upstream/bitcoin ($ref)."
Write-Host "Next: pin a reviewed release tag, then implement the Qitcoin consensus patch set documented in docs/."
