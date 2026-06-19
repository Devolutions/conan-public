#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [string[]] $PackageName = @("libpng", "libjpeg", "libcbor", "mbedtls", "libressl"),
    [string] $ProfileName = "windows-x86_64",
    [switch] $ContinueOnError
)

$ErrorActionPreference = "Stop"

$TestRecipe = Join-Path $PSScriptRoot "test-conan1-recipe.ps1"
$Failures = @()

foreach ($Package in $PackageName) {
    Write-Host ""
    Write-Host "=== Conan 1 second-slice package: $Package ==="
    & $TestRecipe -PackageName $Package -ProfileName $ProfileName
    if ($LASTEXITCODE -ne 0) {
        $Failures += $Package
        if (-not $ContinueOnError) {
            throw "Conan 1 second-slice package failed: $Package"
        }
    }
}

if ($Failures.Count -gt 0) {
    throw "Conan 1 second-slice failures: $($Failures -join ', ')"
}
