#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [string[]] $PackageName = @("cbake", "shared", "openh264", "zlib", "cjson"),
    [string] $HostProfile = "default",
    [string] $BuildProfile = "default",
    [switch] $NoBuildMissing
)

$ErrorActionPreference = "Stop"

$TestRecipe = Join-Path $PSScriptRoot "test-conan2-recipe.ps1"

foreach ($Package in $PackageName) {
    Write-Host ""
    Write-Host "=== Conan 2 first-slice package: $Package ==="

    if ($NoBuildMissing) {
        & $TestRecipe -PackageName $Package -HostProfile $HostProfile -BuildProfile $BuildProfile -NoBuildMissing
    } else {
        & $TestRecipe -PackageName $Package -HostProfile $HostProfile -BuildProfile $BuildProfile
    }
    if ($LASTEXITCODE -ne 0) {
        throw "First-slice package failed: $Package"
    }
}
