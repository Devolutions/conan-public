#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [string[]] $PackageName = @("winpr", "freerdp"),
    [string] $ProfileName = "windows-x86_64",
    [switch] $ContinueOnError
)

$ErrorActionPreference = "Stop"

$TestRecipe = Join-Path $PSScriptRoot "test-conan1-recipe.ps1"
$Failures = @()

foreach ($Package in $PackageName) {
    Write-Host ""
    Write-Host "=== Conan 1 fourth-slice package: $Package ==="
    & $TestRecipe -PackageName $Package -ProfileName $ProfileName
    if ($LASTEXITCODE -ne 0) {
        $Failures += $Package
        if (-not $ContinueOnError) {
            throw "Conan 1 fourth-slice package failed: $Package"
        }
    }
}

if ($Failures.Count -gt 0) {
    throw "Conan 1 fourth-slice failures: $($Failures -join ', ')"
}
