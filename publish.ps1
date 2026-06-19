#!/usr/bin/pwsh

function Invoke-TlkPublish {
	param(
        [ValidateSet('1','2')]
        [string] $ConanMajorVersion,
        [string] $ConanRemoteName,
        [string] $ConanRemoteUrl,
        [string] $ConanUsername,
        [string] $ConanPassword,
        [switch] $DryRun
	)

    if ([string]::IsNullOrEmpty($ConanMajorVersion)) {
        $ConanMajorVersion = if (Test-Path Env:CONAN_MAJOR_VERSION) { $Env:CONAN_MAJOR_VERSION } else { '1' }
    }

    if (-Not $DryRun -And (Test-Path Env:CONAN_PUBLISH_DRY_RUN)) {
        $DryRun = $Env:CONAN_PUBLISH_DRY_RUN -in @('1', 'true', 'True', 'TRUE')
    }

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

    if (-Not $DryRun) {
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
    }

    $Env:CONAN_NON_INTERACTIVE = "1"

    $CacheFolderName = if ($ConanMajorVersion -eq '2') { '.conan2' } else { '.conan' }
    $tarballs = Get-ChildItem . -Filter "*.tar.gz" -Recurse
    $tarballs | ForEach-Object {
        if (-Not (Test-Path $(Join-Path $_.Directory $CacheFolderName))) {
            tar -xf $_.FullName -C $_.Directory
        }
    }

    if ($ConanMajorVersion -eq '2') {
        $ConanCaches = @(Get-ChildItem . -Filter ".conan2" -Hidden -Recurse)

        if ($ConanCaches.Count -eq 0) {
            throw "No Conan 2 caches found to publish"
        }

        $ConanCaches | ForEach-Object {
            $ConanHome = $_.FullName
            $CacheName = $_.Parent.Name
            $ActionName = if ($DryRun) { 'Validating' } else { 'Uploading' }
            Write-Host "$ActionName $CacheName cache with Conan 2"
            $Env:CONAN_HOME="$ConanHome"
            if ($DryRun) {
                conan2 list "*@devolutions/stable"
            } else {
                conan2 remote add $Env:CONAN_REMOTE_NAME $Env:CONAN_REMOTE_URL --force
                conan2 remote login $Env:CONAN_REMOTE_NAME $Env:CONAN_LOGIN_USERNAME --password $Env:CONAN_PASSWORD
                conan2 upload *@devolutions/stable --remote $Env:CONAN_REMOTE_NAME --confirm
            }
        }
    } else {
        $ConanCaches = @(Get-ChildItem . -Filter ".conan" -Hidden -Recurse)

        if ($ConanCaches.Count -eq 0) {
            throw "No Conan 1 caches found to publish"
        }

        $ConanCaches | ForEach-Object {
            $ConanUserHome = $_.Parent
            $CacheName = $ConanUserHome.Name
            $ActionName = if ($DryRun) { 'Validating' } else { 'Uploading' }
            Write-Host "$ActionName $CacheName cache with Conan 1"
            $Env:CONAN_USER_HOME="$ConanUserHome"
            if ($DryRun) {
                conan1 search "*@devolutions/stable"
            } else {
                conan1 remote add $Env:CONAN_REMOTE_NAME $Env:CONAN_REMOTE_URL --force
                conan1 user $Env:CONAN_LOGIN_USERNAME -r $Env:CONAN_REMOTE_NAME -p
                conan1 upload *@devolutions/stable --all --parallel -r $Env:CONAN_REMOTE_NAME -c
            }
        }
    }
}

Invoke-TlkPublish @args
