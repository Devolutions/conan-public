#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [string[]] $PackageName = @("cbake", "shared", "openh264", "zlib", "cjson"),
    [string] $ProfileName = "windows-x86_64"
)

$ErrorActionPreference = "Stop"

$TestRecipe = Join-Path $PSScriptRoot "test-conan1-recipe.ps1"

foreach ($Package in $PackageName) {
    Write-Host ""
    Write-Host "=== Conan 1 first-slice package: $Package ==="
    & $TestRecipe -PackageName $Package -ProfileName $ProfileName
    if ($LASTEXITCODE -ne 0) {
        throw "Conan 1 first-slice package failed: $Package"
    }
}
