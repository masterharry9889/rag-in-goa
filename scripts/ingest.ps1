$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = if ($IsWindows) {
    Join-Path $projectRoot ".venv\Scripts\python.exe"
} else {
    Join-Path $projectRoot ".venv/bin/python"
}

if (-not (Test-Path $pythonPath)) {
    throw "Python virtual environment not found at '$pythonPath'. Create it first with 'python3 -m venv .venv'."
}

Write-Host "Starting ingestion pipeline..."
Write-Host "Using Python: $pythonPath"

# Ensure we are in the project root
Set-Location $projectRoot
$env:PYTHONPATH = $projectRoot

Write-Host "Ensuring project dependencies are installed..."
& $pythonPath -m pip install -r "$projectRoot/requirements.txt"
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed. Fix the pip error above before continuing."
}

Write-Host "Step 1: Building Index (Download, Chunk, Embed, Upsert)"
& $pythonPath "$projectRoot/app/ingestion/build_index.py"
if ($LASTEXITCODE -ne 0) {
    throw "Index build failed."
}

Write-Host "Step 2: Pruning Index (Deduplication)"
& $pythonPath "$projectRoot/app/ingestion/prune_index.py"

Write-Host "Step 3: Database Size Check"
Write-Host "ChromaDB size on disk:"
# Simple equivalent of du -sh for macOS/Linux via PowerShell
Get-ChildItem -Path "$projectRoot/data/chroma" -Recurse -File | Measure-Object -Property Length -Sum | Select-Object @{Name="Size (MB)"; Expression={[math]::round($_.Sum / 1MB, 2)}} | Format-List

Write-Host "Ingestion complete."
