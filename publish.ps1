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

    if (-Not [string]::IsNullOrEmpty($ConanUsername)) {
        $Env:CONAN_LOGIN_USERNAME = $ConanUsername
    }

    if (-Not [string]::IsNullOrEmpty($ConanPassword)) {
        $Env:CONAN_PASSWORD = $ConanPassword
    }

    if (-Not (Test-Path Env:CONAN_REMOTE_NAME)) {
        throw "CONAN_REMOTE_NAME environment variable must be set"
    }

    if (-Not (Test-Path Env:CONAN_REMOTE_URL)) {
        throw "CONAN_REMOTE_URL environment variable must be set"
    }

    if (-Not (Test-Path Env:CONAN_LOGIN_USERNAME)) {
        throw "CONAN_LOGIN_USERNAME environment variable must be set"
    }
    
    if (-Not (Test-Path Env:CONAN_PASSWORD)) {
        throw "CONAN_PASSWORD environment variable must be set"
    }
    
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
        Write-Host "Uploading $CacheName cache"
        $Env:CONAN_USER_HOME="$ConanUserHome"
        conan remote add $Env:CONAN_REMOTE_NAME $Env:CONAN_REMOTE_URL --force
        conan user -p $Env:CONAN_PASSWORD -r $Env:CONAN_REMOTE_NAME $Env:CONAN_LOGIN_USERNAME
        conan upload *@devolutions/stable --all --parallel -r $Env:CONAN_REMOTE_NAME -c
    }
}

Invoke-TlkPublish @args
