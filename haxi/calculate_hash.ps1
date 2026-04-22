# Black2 Hash Calculator - PowerShell Version
# For AI agents on Windows environments
#
# Usage:
#   .\calculate_hash.ps1 <file_path>
#
# Output (JSON format):
#   {"file":"test.txt","size":1024,"sha256":"abc123...","algorithm":"SHA-256"}

param(
    [string]$FilePath
)

if (-not $FilePath) {
    Write-Output "Usage: .\calculate_hash.ps1 <file_path>"
    Write-Output ""
    Write-Output "Calculate SHA-256 hash for Black2 protocol"
    exit 1
}

# Check if file exists
if (-not (Test-Path $FilePath -PathType Leaf)) {
    Write-Output "{`"error`":`"File not found: $FilePath`"}"
    exit 1
}

# Get file info
$FileInfo = Get-Item $FilePath
$FileSize = $FileInfo.Length

# Calculate SHA-256 hash
$HashAlgorithm = [System.Security.Cryptography.SHA256]::Create()
$FileStream = [System.IO.File]::OpenRead($FilePath)
$HashBytes = $HashAlgorithm.ComputeHash($FileStream)
$FileStream.Close()
$HashAlgorithm.Dispose()

# Convert to hex string
$HashString = [BitConverter]::ToString($HashBytes).Replace("-", "").ToLower()

# Output JSON
Write-Output "{`"file`":`"$FilePath`",`"size`":$FileSize,`"sha256`":`"$HashString`",`"algorithm`":`"SHA-256`"}"
