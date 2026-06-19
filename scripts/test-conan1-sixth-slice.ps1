#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [string[]] $PackageName = @("openssh"),
    [string] $ProfileName = "windows-x86_64",
    [switch] $ContinueOnError
)

$ErrorActionPreference = "Stop"

$TestRecipe = Join-Path $PSScriptRoot "test-conan1-recipe.ps1"
$Failures = @()

foreach ($Package in $PackageName) {
    Write-Host ""
    Write-Host "=== Conan 1 sixth-slice package: $Package ==="
    try {
        & $TestRecipe -PackageName $Package -ProfileName $ProfileName
        if ($LASTEXITCODE -ne 0) {
            throw "Conan 1 sixth-slice package failed: $Package"
        }
    } catch {
        $Failures += $Package
        Write-Host $_.Exception.Message
        if (-not $ContinueOnError) {
            throw
        }
    }
}

if ($Failures.Count -gt 0) {
    throw "Conan 1 sixth-slice failures: $($Failures -join ', ')"
}
