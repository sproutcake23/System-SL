# build_msix.ps1 - Build MSIX package from PyInstaller output
# Requires: Windows 10 SDK (for makeappx.exe and signtool.exe)

param(
    [string]$BinaryPath = "..\..\dist\system-sl.exe",
    [string]$OutputDir = "..\..\dist",
    [string]$ManifestPath = "AppxManifest.xml",
    [switch]$Sign,
    [string]$CertPath = "",
    [string]$CertPassword = ""
)

$ErrorActionPreference = "Stop"

# Find Windows SDK tools
$sdkPaths = @(
    "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.22621.0\x64",
    "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.22000.0\x64",
    "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.19041.0\x64"
)

$makeappx = $null
foreach ($path in $sdkPaths) {
    $tool = Join-Path $path "makeappx.exe"
    if (Test-Path $tool) {
        $makeappx = $tool
        break
    }
}

if (-not $makeappx) {
    Write-Error "makeappx.exe not found. Please install Windows 10 SDK."
    exit 1
}

$signtool = $makeappx -replace "makeappx.exe", "signtool.exe"
Write-Host "Using SDK tools from: $(Split-Path $makeappx)"

# Create staging directory
$stagingDir = Join-Path $env:TEMP "msix_staging_$(Get-Random)"
New-Item -ItemType Directory -Path $stagingDir -Force | Out-Null

try {
    Write-Host "Staging MSIX package..."

    # Copy binary
    Copy-Item $BinaryPath -Destination $stagingDir

    # Copy manifest
    Copy-Item $ManifestPath -Destination $stagingDir

    # Create Assets directory
    $assetsDir = Join-Path $stagingDir "Assets"
    New-Item -ItemType Directory -Path $assetsDir -Force | Out-Null

    # Create placeholder icons (1x1 transparent PNGs)
    # In production, replace with actual app icons
    $placeholderPng = [System.Convert]::FromBase64String(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )

    @("StoreLogo.png", "Square150x150Logo.png", "Square44x44Logo.png", "Wide310x150Logo.png", "SplashScreen.png") | ForEach-Object {
        [System.IO.File]::WriteAllBytes((Join-Path $assetsDir $_), $placeholderPng)
    }

    # Build MSIX
    $msixPath = Join-Path $OutputDir "system-sl-windows.msix"
    Write-Host "Creating MSIX package: $msixPath"

    $packArgs = @(
        "pack"
        "/d", $stagingDir
        "/p", $msixPath
        "/o"
    )
    & $makeappx @packArgs

    if ($LASTEXITCODE -ne 0) {
        Write-Error "makeappx failed with exit code $LASTEXITCODE"
        exit 1
    }

    # Sign if requested
    if ($Sign -and $CertPath) {
        Write-Host "Signing MSIX package..."

        $signArgs = @(
            "sign"
            "/fd", "SHA256"
            "/a"
            "/f", $CertPath
        )

        if ($CertPassword) {
            $signArgs += "/p"
            $signArgs += $CertPassword
        }

        $signArgs += $msixPath

        & $signtool @signArgs

        if ($LASTEXITCODE -ne 0) {
            Write-Error "signtool failed with exit code $LASTEXITCODE"
            exit 1
        }
    }

    Write-Host "MSIX package created successfully: $msixPath"
    Write-Host "To install: Right-click the .msix file and select 'Install'"
    Write-Host "Or enable Developer Settings > 'Developer mode' for sideloading"

}
finally {
    # Cleanup staging directory
    Remove-Item -ItemType Directory -Path $stagingDir -Recurse -Force -ErrorAction SilentlyContinue
}
