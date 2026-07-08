#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [ValidateSet("x86", "x86_64", "x64", "arm64", "aarch64")]
    [string[]] $Architecture = @("x86", "x86_64", "arm64"),
    [ValidateSet("Debug", "Release", "RelWithDebInfo")]
    [string[]] $BuildType = @("Debug", "Release", "RelWithDebInfo"),
    [string] $HostProfile = "default",
    [string] $BuildProfile = "default",
    [string] $User = "devolutions",
    [string] $Channel = "stable",
    [string] $CMakeGenerator = "Ninja",
    [switch] $NoBuildMissing,
    [switch] $ContinueOnError,
    [string[]] $ConanArgs = @()
)

$ErrorActionPreference = "Stop"

$TestRecipe = Join-Path $PSScriptRoot "test-conan2-recipe.ps1"
$HostPackages = @("cbake", "shared")
$FullPackages = @(
    "openh264",
    "zlib",
    "cjson",
    "libpng",
    "libjpeg",
    "libcbor",
    "mbedtls",
    "libressl",
    "libfido2",
    "winpr",
    "freerdp",
    "pcre2",
    "libvpx",
    "wxsqlite3"
)
$RelWithDebInfoPackages = @(
    "zlib",
    "cjson",
    "libpng",
    "libjpeg",
    "mbedtls",
    "libressl",
    "winpr",
    "openh264",
    "libcbor",
    "libfido2",
    "freerdp"
)

$Failures = @()

function Invoke-Conan2MatrixRecipe {
    param(
        [Parameter(Mandatory=$true)]
        [string] $RecipeName,
        [Parameter(Mandatory=$true)]
        [string] $TargetArchitecture,
        [Parameter(Mandatory=$true)]
        [string] $TargetBuildType
    )

    $Arguments = @{
        PackageName = $RecipeName
        Architecture = $TargetArchitecture
        BuildType = $TargetBuildType
        HostProfile = $HostProfile
        BuildProfile = $BuildProfile
        User = $User
        Channel = $Channel
        CMakeGenerator = $CMakeGenerator
    }

    if ($NoBuildMissing) {
        $Arguments.NoBuildMissing = $true
    }
    if ($ConanArgs.Count -gt 0) {
        $Arguments.ConanArgs = $ConanArgs
    }

    & $TestRecipe @Arguments
}

foreach ($Package in $HostPackages) {
    Write-Host ""
    Write-Host "=== Conan 2 Windows host package: $Package (x86_64 Release) ==="
    try {
        Invoke-Conan2MatrixRecipe -RecipeName $Package -TargetArchitecture "x86_64" -TargetBuildType "Release"
    } catch {
        $Failures += "host/$Package"
        Write-Host $_.Exception.Message
        if (-not $ContinueOnError) {
            throw
        }
    }
}

foreach ($TargetArchitecture in $Architecture) {
    foreach ($TargetBuildType in $BuildType) {
        $Packages = if ($TargetBuildType -eq "RelWithDebInfo") { $RelWithDebInfoPackages } else { $FullPackages }

        foreach ($Package in $Packages) {
            Write-Host ""
            Write-Host "=== Conan 2 Windows matrix: $TargetArchitecture $TargetBuildType package: $Package ==="
            try {
                Invoke-Conan2MatrixRecipe -RecipeName $Package -TargetArchitecture $TargetArchitecture -TargetBuildType $TargetBuildType
            } catch {
                $Failures += "$TargetArchitecture/$TargetBuildType/$Package"
                Write-Host $_.Exception.Message
                if (-not $ContinueOnError) {
                    throw
                }
            }
        }
    }
}

if ($Failures.Count -gt 0) {
    throw "Conan 2 Windows matrix failures: $($Failures -join ', ')"
}
