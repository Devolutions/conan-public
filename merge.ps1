#!/usr/bin/env pwsh

# Install-Module -Name Join-Object

function Merge-ConanMetadataFile {
    param(
        [Parameter(Mandatory=$true,Position=0)]
        [string] $InputFile,
        [Parameter(Mandatory=$true,Position=1)]
        [string] $OutputFile
    )

    if (Test-Path -Path $OutputFile) {
        $InputObject = Get-Content -Path $InputFile -Raw | ConvertFrom-Json
        $OutputObject = Get-Content -Path $OutputFile -Raw | ConvertFrom-Json
        $InputPackages = $InputObject.packages | Get-Member -MemberType NoteProperty
        foreach ($Package in $InputPackages) {
            $PackageName = $Package.Name
            $PackageValue = $InputObject.packages.$PackageName
            $OutputObject.packages | Add-Member -Type NoteProperty -Name $PackageName -Value $PackageValue -Force
        }
        Set-Content -Path $OutputFile -Value $($OutputObject | ConvertTo-Json -Depth 8) -Force
    } else {
        Copy-Item -Path $InputFile -Destination $OutputFile
    }
}

function Invoke-TlkMerge {
	param(
	)

    $CacheNames = Get-ChildItem -Directory . -Name

    if (Test-Path Env:CONAN_USER_HOME) {
        $ConanDataPath = Join-Path $Env:CONAN_USER_HOME ".conan/data"
    } else {
        $ConanDataPath = "~/.conan/data"
    }
    
    Write-Host "conan data path $ConanDataPath"
    New-Item -Path $ConanDataPath -ItemType Directory -ErrorAction SilentlyContinue | Out-Null
    
    foreach ($CacheName in $CacheNames) {
        Write-Host "Importing $CacheName"
        $PackageNames = Get-ChildItem -Directory "$CacheName/data" -Name
        foreach ($PackageName in $PackageNames) {
            Write-Host "Importing $PackageName ($CacheName)"
            New-Item -Path "$ConanDataPath/$PackageName" -ItemType Directory -ErrorAction SilentlyContinue | Out-Null
            Copy-Item -Path "./$CacheName/data/$PackageName/*" -Destination "$ConanDataPath/$PackageName" `
                -Exclude @('metadata.json', 'metadata.json.lock') -Recurse -Force
        }
        $MetadataFiles = Get-ChildItem -Path $CacheName -Include 'metadata.json' -Recurse -Depth 4 -Name
        foreach ($MetadataFile in $MetadataFiles) {
            $InputFile = "./$CacheName/data/$MetadataFile"
            $OutputFile = "$ConanDataPath/$MetadataFile"
            Merge-ConanMetadataFile $InputFile $OutputFile
        }
    }
}

# upload all packages in the local cache:
# $PackageRefs = $(conan search *devolutions/stable --raw).Split([Environment]::NewLine)
# $PackageRefs | ForEach-Object { conan upload $_ --all -r devolutions-public }

Invoke-TlkMerge @args
