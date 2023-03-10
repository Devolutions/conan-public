#!/usr/bin/env pwsh

# conan remove -f '*'
# conan config install ./settings

function Invoke-ConanRecipe
{
    [CmdletBinding()]
	param(
        [Parameter(Mandatory=$true,Position=0)]
        [string] $PackageName,
        [Parameter(Mandatory=$true)]
        [string] $UserChannel,
        [Parameter(Mandatory=$true)]
        [string] $ProfileName,
        [Parameter(Mandatory=$true)]
        [string] $BuildType,
        [string] $Distribution,
        [string[]] $Aliases
    )

    $Recipes = Join-Path $PSScriptRoot "recipes"
    $PackageVersion = $(Get-Content "$Recipes/$PackageName/VERSION").Trim()
    $PackageReference = "$PackageName/$PackageVersion@$UserChannel"

    Write-Host "building $PackageReference"

    $CreateParams = @(
        "$Recipes/$PackageName",
        $UserChannel,
        "-pr", $ProfileName,
        "-s", "build_type=$BuildType"
    )

    if (-Not [string]::IsNullOrEmpty($Distribution)) {
        $CreateParams += @("-s", "distro=$Distribution")
    }

    & 'conan' 'create' $CreateParams
    
    if ($LASTEXITCODE -ne 0) {
        throw "$PackageName creation failure"
    }

    & 'conan' 'export' "$Recipes/$PackageName" $PackageReference

    foreach ($Alias in $Aliases) {
        & 'conan' 'alias' "$PackageName/$Alias@$UserChannel" $PackageReference
    }
}

function Get-TlkPlatform {
    param(
        [Parameter(Position=0)]
        [string] $Platform
    )

    if (-Not $Platform) {
        $Platform = if ($IsWindows) {
            'windows'
        } elseif ($IsMacOS) {
            'macos'
        } elseif ($IsLinux) {
            'linux'
        }
    }

    $Platform
}

function Invoke-TlkBuild {
	param(
		[ValidateSet('windows','macos','linux','ios','android')]
		[string] $Platform,
		[ValidateSet('x86','x86_64','arm','arm64','aarch64')]
		[string] $Architecture = "x86_64",
		[ValidateSet('ubuntu-18.04','ubuntu-20.04','debian-10','alpine-3.14','opensuse-15.2')]
		[string] $Distribution,
        [string] $UserChannel = "devolutions/stable",
        [ValidateSet('Release','RelWithDebInfo','Debug','Both')] # Both == Release + Debug
		[string] $BuildType = "Release"
	)

    $HostPlatform = Get-TlkPlatform
    $HostArchitecture = "x86_64"
    $HostProfile = "$HostPlatform-$HostArchitecture".ToLower()

    if (-Not $Platform) {
        $Platform = $HostPlatform
    }

    if ($Architecture -eq 'aarch64') {
        $Architecture = 'arm64'
    }

    if (($Platform -eq 'linux') -And (-Not $Distribution)) {
        $Distribution = "ubuntu-18.04"
    }

    $HostPackages = @(
        'cbake',
        'shared'
    )

    $HostPackages += @('yarc')
    #$HostPackages += @('clang-llvm')
    $HostPackages += @('halide')

    $TargetPackages = @()

    if ($Platform -eq 'Linux') {
        $TargetPackages += @('sysroot')
    }

    $TargetPackages += @(
        'zlib',
        'lz4',
        'miniz',
        'lizard',
        'libpng',
        'libjpeg',
        'libcbor',
        'mbedtls',
        'openssl',
        'libressl',
        'winpr',
        'freerdp',
        'pcre2',
        'nng',
        'curl'
    )

    if (@('linux','android') -Contains $Platform) {
        $TargetPackages += @(
            'libudev-zero'
        )
    }

    if (@('windows','macos','linux') -Contains $Platform) {
        $TargetPackages += @(
            'munit',
            'libvpx',
            'libwebm',
            'libfido2',
            'wxsqlite3'
        )
    }

    if (@('windows','macos','linux') -Contains $Platform) {
        $TargetPackages += @('openssh')
    }

    if ($Platform -eq 'windows') {
        $TargetPackages += @('crashpad')
    }

    if ((($Platform -eq 'Android') -Or ($Platform -eq "macos")) -And ($BuildType -eq 'RelWithDebInfo')) {
        $TargetPackages = @(
          'zlib', 
          'libpng',
          'libjpeg',
          'mbedtls', 
          'openssl', 
          'winpr', 
          'freerdp'
        )
    }

    $TargetProfile = "$Platform-$Architecture".ToLower()
    $Aliases = @('latest')

    foreach ($Package in $HostPackages) {
        $params = @{
            PackageName = $Package;
            UserChannel = $UserChannel;
            ProfileName = $HostProfile;
            BuildType = 'Release';
            Aliases = $Aliases;
        }
        Invoke-ConanRecipe @params
    }

    foreach ($Package in $TargetPackages) {
        $params = @{
            PackageName = $Package;
            UserChannel = $UserChannel;
            ProfileName = $TargetProfile;
            BuildType = $BuildType;
            Aliases = $Aliases;
        }
        if (-Not [string]::IsNullOrEmpty($Distribution)) {
            $params['Distribution'] = $Distribution;
        }

        if ($BuildType -eq 'Both') {
            $params['BuildType'] = 'Release'
            Invoke-ConanRecipe @params

            $params['BuildType'] = 'Debug'
            Invoke-ConanRecipe @params
        } else {
            Invoke-ConanRecipe @params
        }
    }
}

Invoke-TlkBuild @args