#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string] $PackageName,
    [string] $ProfileName = "windows-x86_64",
    [ValidateSet("windows", "linux", "macos", "ios", "iossimulator", "android")]
    [string] $Platform = "windows",
    [ValidateSet("x86", "x86_64", "x64", "arm64", "aarch64")]
    [string] $Architecture = "x86_64",
    [ValidateSet("Debug")]
    [string] $BuildType = "Debug",
    [string] $UserChannel = "devolutions/stable",
    [string[]] $Aliases = @("latest")
)

$ErrorActionPreference = "Stop"

function Get-Conan1Command {
    $Command = @(Get-Command "conan1" -CommandType Application -ErrorAction SilentlyContinue)[0]
    if ($Command) {
        return $Command.Source
    }

    if ($IsWindows) {
        $Shim = Join-Path (Join-Path (Join-Path $HOME ".local") "bin") "conan1.cmd"
        if (Test-Path $Shim) {
            return $Shim
        }
    } else {
        $Shim = Join-Path (Join-Path (Join-Path $HOME ".local") "bin") "conan1"
        if (Test-Path $Shim) {
            return $Shim
        }
    }

    throw "conan1 was not found. Run .\scripts\setup-conan-venvs.ps1 and open a new terminal."
}

function Invoke-Conan1 {
    param(
        [Parameter(Mandatory=$true)]
        [string] $Conan,
        [string[]] $Arguments = @()
    )

    & $Conan @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "conan1 failed with exit code $LASTEXITCODE`: conan1 $($Arguments -join ' ')"
    }
}

function ConvertTo-Conan1ProfileArchitecture {
    param([string] $Architecture)

    switch ($Architecture) {
        "x64" { return "x86_64" }
        default { return $Architecture }
    }
}

function Get-Conan1ProfileName {
    param(
        [Parameter(Mandatory=$true)]
        [string] $Platform,
        [Parameter(Mandatory=$true)]
        [string] $Architecture
    )

    $ProfileArchitecture = ConvertTo-Conan1ProfileArchitecture $Architecture
    return "$Platform-$ProfileArchitecture"
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Recipes = Join-Path (Join-Path $RepoRoot "conan1") "recipes"
$RecipePath = Join-Path $Recipes $PackageName
if (-not (Test-Path $RecipePath)) {
    throw "Conan 1 recipe '$PackageName' was not found at $RecipePath."
}

$Version = (Get-Content (Join-Path $RecipePath "VERSION")).Trim()
$PackageReference = "$PackageName/$Version@$UserChannel"
$Conan = Get-Conan1Command

if (-not $PSBoundParameters.ContainsKey("ProfileName")) {
    $ProfileName = Get-Conan1ProfileName $Platform $Architecture
}

Write-Host "Testing Conan 1 recipe '$PackageName' with profile $ProfileName and $BuildType"
Invoke-Conan1 $Conan @(
    "create",
    $RecipePath,
    $UserChannel,
    "-pr", $ProfileName,
    "-s", "build_type=$BuildType"
)

Invoke-Conan1 $Conan @("export", $RecipePath, $PackageReference)

foreach ($Alias in $Aliases) {
    Invoke-Conan1 $Conan @("alias", "$PackageName/$Alias@$UserChannel", $PackageReference)
}
