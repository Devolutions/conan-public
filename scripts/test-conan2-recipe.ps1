#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string] $PackageName,
    [ValidateSet("windows", "linux", "macos", "ios", "android")]
    [string] $Platform = "windows",
    [ValidateSet("x86", "x86_64", "x64", "arm", "arm64", "aarch64")]
    [string] $Architecture = "x86_64",
    [ValidateSet("Debug", "Release", "RelWithDebInfo")]
    [string] $BuildType = "Debug",
    [string] $HostProfile = "default",
    [string] $BuildProfile = "default",
    [string] $User = "devolutions",
    [string] $Channel = "stable",
    [string] $CMakeGenerator = "Ninja",
    [switch] $NoBuildMissing,
    [string[]] $ConanArgs = @()
)

$ErrorActionPreference = "Stop"

function Get-Conan2Command {
    $Command = @(Get-Command "conan2" -CommandType Application -ErrorAction SilentlyContinue)[0]
    if ($Command) {
        return $Command.Source
    }

    if ($IsWindows) {
        $Shim = Join-Path (Join-Path (Join-Path $HOME ".local") "bin") "conan2.cmd"
        if (Test-Path $Shim) {
            return $Shim
        }
    } else {
        $Shim = Join-Path (Join-Path (Join-Path $HOME ".local") "bin") "conan2"
        if (Test-Path $Shim) {
            return $Shim
        }
    }

    throw "conan2 was not found. Run .\scripts\setup-conan-venvs.ps1 and open a new terminal."
}

function ConvertTo-ConanArchitecture {
    param([string] $Architecture)

    switch ($Architecture) {
        "x64" { return "x86_64" }
        "arm" { return "armv7" }
        "arm64" { return "armv8" }
        "aarch64" { return "armv8" }
        default { return $Architecture }
    }
}

function ConvertTo-ConanOs {
    param([string] $Platform)

    switch ($Platform) {
        "windows" { return "Windows" }
        "linux" { return "Linux" }
        "macos" { return "Macos" }
        "ios" { return "iOS" }
        "android" { return "Android" }
        default { throw "Unsupported platform '$Platform'." }
    }
}

function Get-ConanPlatformSettings {
    param(
        [Parameter(Mandatory=$true)]
        [string] $Platform,
        [Parameter(Mandatory=$true)]
        [string] $Architecture
    )

    switch ($Platform) {
        "android" {
            return @(
                "os.api_level=21",
                "compiler=clang",
                "compiler.version=18",
                "compiler.libcxx=c++_static"
            )
        }
        "ios" {
            $Sdk = if ($Architecture -eq "x86_64") { "iphonesimulator" } else { "iphoneos" }
            return @("os.version=9.3", "os.sdk=$Sdk")
        }
        "macos" {
            $Version = if ($Architecture -in @("armv8", "arm64", "aarch64")) { "10.15" } else { "10.9" }
            return @("os.version=$Version")
        }
        default {
            return @()
        }
    }
}

function Get-ConanPlatformConf {
    param([string] $Platform)

    if ($Platform -eq "android") {
        $NdkPath = if ($Env:ANDROID_NDK_HOME) { $Env:ANDROID_NDK_HOME } else { $Env:ANDROID_NDK_ROOT }
        if (-not [string]::IsNullOrWhiteSpace($NdkPath)) {
            return @("tools.android:ndk_path=$NdkPath")
        }
    }

    return @()
}

function Get-VcVarsTarget {
    param([string] $Architecture)

    switch ($Architecture) {
        "x86" { return "x64_x86" }
        "x86_64" { return "x64" }
        "x64" { return "x64" }
        "arm64" { return "x64_arm64" }
        "aarch64" { return "x64_arm64" }
        default { throw "Unsupported Windows architecture '$Architecture'." }
    }
}

function Get-VcVarsAllCommand {
    param([string] $Architecture)

    $Candidates = @()
    $VsWhere = Get-Command "vswhere" -CommandType Application -ErrorAction SilentlyContinue
    if ($VsWhere) {
        $InstallationPath = & $VsWhere.Source -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($InstallationPath)) {
            $Candidates += Join-Path $InstallationPath "VC\Auxiliary\Build\vcvarsall.bat"
        }
    }

    $Candidates += @(
        "C:\Program Files\Microsoft Visual Studio\18\Professional\VC\Auxiliary\Build\vcvarsall.bat",
        "C:\Program Files\Microsoft Visual Studio\18\Enterprise\VC\Auxiliary\Build\vcvarsall.bat",
        "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat",
        "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat",
        "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat",
        "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
    )

    foreach ($Candidate in $Candidates) {
        if (Test-Path $Candidate) {
            return $Candidate
        }
    }

    $Command = Get-Command "cl" -CommandType Application -ErrorAction SilentlyContinue
    if ($Command -and (Get-VcVarsTarget $Architecture) -eq "x64") {
        return $null
    }

    throw "No Visual Studio vcvarsall.bat was detected for Windows $Architecture."
}

function ConvertTo-CmdArgument {
    param([string] $Value)

    '"{0}"' -f ($Value -replace '"', '\"')
}

function Invoke-Conan2 {
    param(
        [Parameter(Mandatory=$true)]
        [string] $Conan,
        [string[]] $Arguments = @(),
        [string] $Architecture = "x86_64",
        [string] $Platform = "windows"
    )

    $VcVarsAll = if ($IsWindows -and $Platform -eq "windows") { Get-VcVarsAllCommand $Architecture } else { $null }
    if ($VcVarsAll) {
        $VcVarsTarget = Get-VcVarsTarget $Architecture
        $Command = @(
            "call",
            (ConvertTo-CmdArgument $VcVarsAll),
            $VcVarsTarget,
            ">nul",
            "&&",
            (ConvertTo-CmdArgument $Conan)
        ) + ($Arguments | ForEach-Object { ConvertTo-CmdArgument $_ })

        & $env:ComSpec /d /s /c ($Command -join " ")
    } else {
        & $Conan @Arguments
    }

    if ($LASTEXITCODE -ne 0) {
        throw "conan2 failed with exit code $LASTEXITCODE`: conan2 $($Arguments -join ' ')"
    }
}

function Ensure-Conan2Profile {
    param(
        [Parameter(Mandatory=$true)]
        [string] $Conan,
        [Parameter(Mandatory=$true)]
        [string] $ProfileName
    )

    $ProfilePath = Join-Path (Join-Path (Join-Path $HOME ".conan2") "profiles") $ProfileName
    if (Test-Path $ProfilePath) {
        return
    }

    if ($ProfileName -ne "default") {
        throw "Conan 2 profile '$ProfileName' does not exist at $ProfilePath."
    }

    Invoke-Conan2 $Conan @("profile", "detect", "--force")
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RecipePath = Join-Path (Join-Path $RepoRoot "conan2\recipes") $PackageName
if (-not (Test-Path $RecipePath)) {
    throw "Conan 2 recipe '$PackageName' was not found at $RecipePath."
}

$Conan = Get-Conan2Command
$ConanArchitecture = ConvertTo-ConanArchitecture $Architecture
$ConanOs = ConvertTo-ConanOs $Platform
$PlatformSettings = Get-ConanPlatformSettings $Platform $ConanArchitecture
$PlatformConf = Get-ConanPlatformConf $Platform
Ensure-Conan2Profile $Conan $HostProfile
Ensure-Conan2Profile $Conan $BuildProfile

$CreateArgs = @(
    "create",
    $RecipePath,
    "-nr",
    "--user", $User,
    "--channel", $Channel,
    "-pr:h", $HostProfile,
    "-pr:b", $BuildProfile,
    "-s:h", "os=$ConanOs",
    "-s:h", "arch=$ConanArchitecture",
    "-s:h", "build_type=$BuildType",
    "-c:h", "tools.cmake.cmaketoolchain:generator=$CMakeGenerator"
)

foreach ($Setting in $PlatformSettings) {
    $CreateArgs += @("-s:h", $Setting)
}

foreach ($Conf in $PlatformConf) {
    $CreateArgs += @("-c:h", $Conf)
}

if (-not $NoBuildMissing) {
    $CreateArgs += "--build=missing"
}

$CreateArgs += $ConanArgs

Write-Host "Testing Conan 2 recipe '$PackageName' for $ConanOs $Architecture ($ConanArchitecture) $BuildType"
Invoke-Conan2 $Conan $CreateArgs $Architecture $Platform
