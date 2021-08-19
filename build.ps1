
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
        [string[]] $Aliases
    )

    $PackageVersion = $(Get-Content "./recipes/$PackageName/VERSION").Trim()
    $PackageReference = "$PackageName/$PackageVersion@$UserChannel"

    Write-Host "Building $PackageReference package"

    & 'conan' 'create' "./recipes/$PackageName" $UserChannel -pr $ProfileName -s build_type=Release
    
    if ($LASTEXITCODE -ne 0) {
        throw "$PackageName creation failure"
    }

    & 'conan' 'export' "./recipes/$PackageName" $PackageReference

    foreach ($Alias in $Aliases) {
        & 'conan' 'alias' "$PackageName/$Alias@$UserChannel" $PackageReference
    }
}

$UserChannel = "devolutions/stable"
$ProfileName = "linux-x86_64"

$Packages = @(
    'cbake',
    'utils',
    'lipo', # TODO: merge with utils
    'rustup', # TODO: merge with utils
    'yarc',
    'zlib',
    'lz4',
    'miniz',
    'munit',
    'lizard',
    'libpng',
    'libjpeg',
    'mbedtls',
    'openssl',
    'winpr',
    'freevnc',
    'freerdp',
    'pcre2',
    'nng'
    )

foreach ($Package in $Packages) {
    Invoke-ConanRecipe $Package -UserChannel $UserChannel -ProfileName $ProfileName -Aliases @('latest')
}
