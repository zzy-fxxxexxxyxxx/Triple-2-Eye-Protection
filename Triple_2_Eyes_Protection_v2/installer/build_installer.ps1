$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$issPath = Join-Path $PSScriptRoot "Triple2EyeProtection.iss"

if (-not (Test-Path $issPath)) {
    throw "Installer script not found: $issPath"
}

$distPath = Join-Path $root "dist\Triple 2 Eye Protection\Triple 2 Eye Protection.exe"
if (-not (Test-Path $distPath)) {
    throw "PyInstaller output missing. Build dist/Triple 2 Eye Protection first."
}

$iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue

if (-not $iscc) {
    $candidatePaths = @(
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe",
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe")
    )

    $resolved = $candidatePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($resolved) {
        $iscc = [PSCustomObject]@{ Source = $resolved }
    }
}

if (-not $iscc) {
    throw "ISCC.exe not found. Please install Inno Setup 6."
}

Write-Host "Using ISCC:" $iscc.Source
& $iscc.Source $issPath

if ($LASTEXITCODE -ne 0) {
    throw "ISCC build failed with exit code $LASTEXITCODE"
}

Write-Host "Installer build completed. Output folder: $root\installer_output"
