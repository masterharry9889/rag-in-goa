$ErrorActionPreference = "Stop"

Write-Host "Starting ingestion pipeline..."

# Ensure we are in the project root
$env:PYTHONPATH = "."

Write-Host "Step 1: Building Index (Download, Chunk, Embed, Upsert)"
python app/ingestion/build_index.py

Write-Host "Step 2: Pruning Index (Deduplication)"
python app/ingestion/prune_index.py

Write-Host "Step 3: Database Size Check"
Write-Host "ChromaDB size on disk:"
# Simple equivalent of du -sh for Windows PowerShell
Get-ChildItem -Path "data/chroma" -Recurse -File | Measure-Object -Property Length -Sum | Select-Object @{Name="Size (MB)"; Expression={[math]::round($_.Sum / 1MB, 2)}} | Format-List

Write-Host "Ingestion complete."
