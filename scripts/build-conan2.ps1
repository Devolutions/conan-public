#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [ValidateSet("windows", "linux", "macos", "ios", "iossimulator", "android")]
    [string] $Platform = "linux",
    [ValidateSet("x86", "x86_64", "x64", "arm", "arm64", "aarch64")]
    [string] $Architecture = "x86_64",
    [ValidateSet("Debug", "Release", "RelWithDebInfo", "Both")]
    [string] $BuildType = "Debug",
    [ValidateSet("ubuntu-18.04", "ubuntu-20.04", "ubuntu-22.04", "ubuntu-24.04", "debian-10", "debian-11", "debian-12", "alpine-3.14", "alpine-3.17", "alpine-3.21", "rhel8", "rhel9")]
    [string] $Distribution = "ubuntu-20.04",
    [string] $HostProfile = "default",
    [string] $BuildProfile = "default",
    [string] $User = "devolutions",
    [string] $Channel = "stable",
    [string[]] $PackageName = @(),
    [switch] $NoBuildMissing
)

$ErrorActionPreference = "Stop"

$TestRecipe = Join-Path $PSScriptRoot "test-conan2-recipe.ps1"

function ConvertTo-SysrootTargetArchitecture {
    param([string] $Architecture)

    switch ($Architecture) {
        "x64" { return "x86_64" }
        "aarch64" { return "armv8" }
        "arm64" { return "armv8" }
        default { return $Architecture }
    }
}


function Get-DefaultPackageList {
    param(
        [Parameter(Mandatory=$true)]
        [string] $Platform,
        [Parameter(Mandatory=$true)]
        [string] $BuildType
    )

    $BasePackagesEarly = @("zlib", "cjson", "libpng", "libjpeg", "libcbor", "mbedtls", "libressl")
    $BasePackagesLate = @("winpr", "freerdp", "pcre2")

    $Packages = @("cbake", "shared")

    if ($Platform -eq "linux") {
        $Packages += "sysroot"
        $Packages += "webview"
        $Packages += "embedded-terminal"
    }

    if ($BuildType -eq "RelWithDebInfo" -and $Platform -in @("windows", "macos", "android")) {
        $Packages += @("zlib", "cjson", "libpng", "libjpeg", "mbedtls", "libressl", "winpr")
        if ($Platform -in @("windows", "macos")) {
            $Packages += @("openh264", "libcbor", "libfido2")
        }
        $Packages += "freerdp"
        return $Packages
    }

    if ($Platform -in @("windows", "macos", "linux")) {
        $Packages += "openh264"
    }

    $Packages += $BasePackagesEarly

    if ($Platform -in @("windows", "macos", "linux")) {
        $Packages += "libfido2"
    }

    $Packages += $BasePackagesLate

    if ($Platform -in @("linux", "android")) {
        $Packages += "libudev-zero"
    }

    if ($Platform -in @("windows", "macos", "linux")) {
        $Packages += @("libvpx", "wxsqlite3")
    }

    return $Packages
}

if ($PackageName.Count -eq 0) {
    $PackageName = Get-DefaultPackageList $Platform $BuildType
}

foreach ($Package in $PackageName) {
    $EffectiveBuildTypes = if ($BuildType -eq "Both") { @("Release", "Debug") } else { @($BuildType) }

    foreach ($EffectiveBuildType in $EffectiveBuildTypes) {
        Write-Host ""
        Write-Host "=== Conan 2 package: $Package ($EffectiveBuildType) ==="

        $Arguments = @{
            PackageName = $Package
            Platform = $Platform
            Architecture = $Architecture
            BuildType = $EffectiveBuildType
            HostProfile = $HostProfile
            BuildProfile = $BuildProfile
            User = $User
            Channel = $Channel
        }

        if ($NoBuildMissing) {
            $Arguments.NoBuildMissing = $true
        }

        if ($Package -eq "sysroot") {
            $SysrootTargetArchitecture = ConvertTo-SysrootTargetArchitecture $Architecture
            $Arguments.ConanArgs = @(
                "-o:h", "sysroot/*:source=prebuilt",
                "-o:h", "sysroot/*:distro=$Distribution",
                "-o:h", "sysroot/*:target_arch=$SysrootTargetArchitecture"
            )
        } elseif ($Platform -eq "linux" -and $Package -notin @("cbake", "shared")) {
            $SysrootTargetArchitecture = ConvertTo-SysrootTargetArchitecture $Architecture
            $Arguments.ConanArgs = @(
                "-o:b", "sysroot/*:source=prebuilt",
                "-o:b", "sysroot/*:distro=$Distribution",
                "-o:b", "sysroot/*:target_arch=$SysrootTargetArchitecture"
            )
        }

        & $TestRecipe @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Conan 2 package failed: $Package ($EffectiveBuildType)"
        }
    }
}