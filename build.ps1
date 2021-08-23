
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
        [string[]] $Aliases
    )

    $Recipes = Join-Path $PSScriptRoot "recipes"
    $PackageVersion = $(Get-Content "$Recipes/$PackageName/VERSION").Trim()
    $PackageReference = "$PackageName/$PackageVersion@$UserChannel"

    & 'conan' 'create' "$Recipes/$PackageName" $UserChannel -pr $ProfileName -s build_type=$BuildType
    
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
		[ValidateSet('x86','x86_64','arm64','aarch64')]
		[string] $Architecture = "x86_64",
        [string] $UserChannel = "devolutions/stable",
        [ValidateSet('Release','Debug')]
		[string] $BuildType = "Release",
        [switch] $IncludePrivate
	)

    $HostPlatform = Get-TlkPlatform
    $HostArchitecture = "x86_64"
    $HostProfile = "$HostPlatform-$HostArchitecture".ToLower()

    if (-Not $Platform) {
        $Platform = $HostPlatform
    }

    $HostPackages = @(
        'cbake',
        'shared'
    )

    if ($IsLinux) {
        $HostPackages += @('sysroot')
    }

    $HostPackages += @('yarc')

    #$HostPackages += @('clang-llvm', 'halide')

    if ($IsWindows) {
        #$HostPackages += @('msys2')
    }

    $TargetPackages = @(
        'zlib',
        'lz4',
        'miniz',
        'lizard',
        'libpng',
        'libjpeg',
        'mbedtls',
        'openssl',
        'winpr',
        'freerdp',
        'pcre2',
        'nng',
        'curl',
        'libyuv'
    )

    #$TargetPackages += @('xpp')

    if (@('windows','macos','linux') -Contains $Platform) {
        $TargetPackages += @(
            'munit',
            'libvpx',
            'libwebm',
            'jetsocat',
            'siquery'
        )
    }

    if ($IsWindows) {
        $TargetPackages += @('crashpad')
    }

    if ($IncludePrivate) {
        $TargetPackages += @('freevnc')
    }

    $TargetProfile = "$Platform-$Architecture".ToLower()
    $Aliases = @('latest')

    foreach ($Package in $HostPackages) {
        $params = @{
            PackageName = $Package;
            UserChannel = $UserChannel;
            ProfileName = $HostProfile;
            BuildType = $BuildType;
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
        Invoke-ConanRecipe @params
    }
}

Invoke-TlkBuild @args
