$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $RepoRoot
try {
    python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
    python scripts/export_calm.py --check
    if ($LASTEXITCODE -ne 0) { throw 'Architecture validation failed' }
} finally { Pop-Location }
