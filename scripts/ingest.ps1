$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$isWindows = $IsWindows -or $env:OS -eq "Windows_NT" -or [System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT
$supportedPythonVersions = @("3.11", "3.12")

function Get-VenvPythonPath {
    $pythonCandidates = @(
        if ($isWindows) {
            Join-Path $projectRoot ".venv\Scripts\python.exe"
            Join-Path $projectRoot ".venv\Scripts\python"
        } else {
            Join-Path $projectRoot ".venv/bin/python"
            Join-Path $projectRoot ".venv/bin/python3"
        }
    )

    return ($pythonCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1)
}

function Get-PythonVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PythonPath
    )

    try {
        $versionText = & $PythonPath -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"
        return $versionText.Trim()
    }
    catch {
        return $null
    }
}

function New-SupportedVenv {
    $commands = @()

    foreach ($version in @("3.12", "3.11")) {
        if ($isWindows) {
            if (Get-Command "py" -ErrorAction SilentlyContinue) {
                $commands += "py -$version -m venv .venv"
            }
        }

        $pythonAlias = if ($version -eq "3.12") { "python3.12" } else { "python3.11" }
        if (Get-Command $pythonAlias -ErrorAction SilentlyContinue) {
            $commands += "$pythonAlias -m venv .venv"
        }
    }

    if ($commands.Count -eq 0) {
        $commands = if ($isWindows) {
            @(
                "python -m venv .venv",
                "python3 -m venv .venv"
            )
        } else {
            @(
                "python3 -m venv .venv",
                "python -m venv .venv"
            )
        }
    }

    foreach ($command in $commands) {
        try {
            $venvDir = Join-Path $projectRoot ".venv"
            if (Test-Path $venvDir) {
                Remove-Item -LiteralPath $venvDir -Recurse -Force
            }

            Push-Location $projectRoot
            Invoke-Expression $command
            $newVenvPath = Get-VenvPythonPath
            if ($newVenvPath) {
                return $newVenvPath
            }
        }
        finally {
            Pop-Location
        }
    }

    throw "Could not create a supported virtual environment with Python 3.11 or 3.12."
}

$pythonPath = Get-VenvPythonPath
if (-not $pythonPath) {
    Write-Host "Python virtual environment not found. Creating one with a supported Python version..."
    $pythonPath = New-SupportedVenv
}

$pythonVersion = Get-PythonVersion -PythonPath $pythonPath
if ($pythonVersion -and $pythonVersion -notin $supportedPythonVersions) {
    Write-Host "Detected Python $pythonVersion in '$pythonPath'. This project requires Python 3.11 or 3.12. Recreating the virtual environment..."
    $pythonPath = New-SupportedVenv
    $pythonVersion = Get-PythonVersion -PythonPath $pythonPath
}

if (-not $pythonVersion -or $pythonVersion -notin $supportedPythonVersions) {
    throw "Unsupported Python version '$pythonVersion' found at '$pythonPath'. Recreate the virtual environment with Python 3.11 or 3.12."
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
