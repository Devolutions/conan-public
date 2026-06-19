#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [string[]] $PackageName = @("pcre2", "libvpx", "wxsqlite3"),
    [string] $HostProfile = "default",
    [string] $BuildProfile = "default",
    [switch] $NoBuildMissing
)

$ErrorActionPreference = "Stop"

$TestRecipe = Join-Path $PSScriptRoot "test-conan2-recipe.ps1"

foreach ($Package in $PackageName) {
    Write-Host ""
    Write-Host "=== Conan 2 fifth-slice package: $Package ==="

    if ($NoBuildMissing) {
        & $TestRecipe -PackageName $Package -HostProfile $HostProfile -BuildProfile $BuildProfile -NoBuildMissing
    } else {
        & $TestRecipe -PackageName $Package -HostProfile $HostProfile -BuildProfile $BuildProfile
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Conan 2 fifth-slice package failed: $Package"
    }
}
