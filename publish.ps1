#!/usr/bin/pwsh

function Invoke-TlkPublish {
	param(
        [string] $ConanRemoteName,
        [string] $ConanRemoteUrl,
        [string] $ConanUsername,
        [string] $ConanPassword
	)

    if (-Not [string]::IsNullOrEmpty($ConanRemoteName)) {
        $Env:CONAN_REMOTE_NAME = $ConanRemoteName
    }

    if (-Not [string]::IsNullOrEmpty($ConanRemoteUrl)) {
        $Env:CONAN_REMOTE_URL = $ConanRemoteUrl
    }

    if (-Not (Test-Path Env:CONAN_REMOTE_NAME)) {
        throw "CONAN_REMOTE_NAME environment variable must be set"
    }

    if (-Not (Test-Path Env:CONAN_REMOTE_URL)) {
        throw "CONAN_REMOTE_URL environment variable must be set"
    }

    $ConanRemoteName = $Env:CONAN_REMOTE_NAME
    $ConanRemoteUrl = $Env:CONAN_REMOTE_URL
    Write-Host "conan remote name: $ConanRemoteName"
    Write-Host "conan remote url: $ConanRemoteUrl"

    $tarballs = Get-ChildItem . -Filter "*.tar.gz" -Recurse
    $tarballs | ForEach-Object {
        if (-Not (Test-Path $(Join-Path $_.Directory '.conan'))) {
            tar -xf $_.FullName -C $_.Directory
        }
    }
    
    $ConanCaches = Get-ChildItem . -Filter ".conan" -Hidden -Recurse
    
    $ConanCaches | ForEach-Object {
        $ConanUserHome = $_.Parent
        $CacheName = $ConanUserHome.Name
        $Env:CONAN_USER_HOME="$ConanUserHome"
        Write-Host "Uploading $CacheName cache"

        conan remote add $ConanRemoteName $ConanRemoteUrl --force
        conan remote list

        conan user -r $ConanRemoteName -p

        if ($LASTEXITCODE -ne 0) {
            throw "conan user failure!"
        }

        conan upload *@devolutions/stable --all --parallel -r $ConanRemoteName -c

        if ($LASTEXITCODE -ne 0) {
            throw "conan upload failure!"
        }
    }
}

Invoke-TlkPublish @args
