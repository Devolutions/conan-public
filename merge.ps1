#!/usr/bin/env pwsh

$CacheNames = Get-ChildItem -Directory . -Name

if (Test-Path Env:CONAN_USER_HOME) {
    $ConanDataPath = Join-Path $Env:CONAN_USER_HOME ".conan/data"
} else {
    $ConanDataPath = ".conan/data"
}

Write-Host "conan data path $ConanDataPath"
New-Item -Path $ConanDataPath -ItemType Directory -ErrorAction SilentlyContinue | Out-Null

foreach ($CacheName in $CacheNames) {
    Write-Host "Importing $CacheName"
    $PackageNames = Get-ChildItem -Directory $CacheName -Name
    foreach ($PackageName in $PackageNames) {
        Write-Host "Importing $PackageName ($CacheName)"
        New-Item -Path "./$ConanDataPath/$PackageName" -ItemType Directory -ErrorAction SilentlyContinue | Out-Null
        Copy-Item -Path "./$CacheName/$PackageName/*" -Destination "./$ConanDataPath/$PackageName" -Recurse -Force
    }
}

# upload all packages in the local cache:
# $PackageRefs = $(conan search *devolutions/stable --raw).Split([Environment]::NewLine)
# $PackageRefs | ForEach-Object { conan upload $_ --all -r devolutions-public }
