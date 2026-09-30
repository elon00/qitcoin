# Qitcoin Release Packaging Script (Windows PowerShell)
$ErrorActionPreference = "Stop"

$version = "0.1.0-rc1"
$distDir = "dist"
$packageName = "qitcoin-$version-win64"

Write-Host "=== Packaging Qitcoin Release $version for Windows ==="
New-Item -ItemType Directory -Force -Path "$distDir\$packageName\bin" | Out-Null
New-Item -ItemType Directory -Force -Path "$distDir\$packageName\doc" | Out-Null

# Copy configs and docs
Copy-Item "docker\*.conf" "$distDir\$packageName\" -ErrorAction SilentlyContinue
Copy-Item "README.md", "LICENSE" "$distDir\$packageName\"
Copy-Item "docs\*.md" "$distDir\$packageName\doc\"

# Archive
$zipPath = "$distDir\$packageName.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path "$distDir\$packageName\*" -DestinationPath $zipPath -Force

$hash = (Get-FileHash -Path $zipPath -Algorithm SHA256).Hash
Set-Content -Path "$zipPath.sha256" -Value "$hash  $packageName.zip"

Write-Host "Release package created: $zipPath"
Write-Host "SHA-256: $hash"
