# Devolutions Conan public recipes

This repository contains the [Conan](https://conan.io/) build recipes for Devolutions. Conan 1 remains supported while Conan 2 runs in parallel for the migrated package set.

## Repository layout

| Path | Purpose |
| --- | --- |
| `conan1\recipes` | Existing Conan 1 recipes. These stay functional and serve as the migration reference. |
| `conan2\recipes` | Conan 2 recipes. Add and expand migrated recipes here one at a time after testing. |
| `settings` | Current Conan 1 configuration and profiles. |
| `scripts\setup-conan-venvs.ps1` | Creates isolated Conan 1 and Conan 2 virtual environments plus `conan1` and `conan2` shims. |

Avoid using an unqualified `conan` command in this repository. Use `conan1` for existing recipes and `conan2` for migrated recipes.

## Fresh Windows setup

Install Python 3, then run the setup script from the repository root:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\setup-conan-venvs.ps1
```

The script creates:

| Alias | Virtual environment | Conan version |
| --- | --- | --- |
| `conan1` | `%USERPROFILE%\.conan-venvs\conan1` | `1.66.0` |
| `conan2` | `%USERPROFILE%\.conan-venvs\conan2` | latest `2.x` |

It writes shims to `%USERPROFILE%\.local\bin` and adds that directory to the user PATH when missing. Open a new terminal after setup, then verify:

```powershell
conan1 --version
conan2 --version
```

If you do not want the script to update your user PATH, run it with `-NoUserPathUpdate` and add the shim directory manually.

## Fresh WSL/Linux setup

Work from the native Linux checkout, not a Windows-mounted worktree. Install the local build prerequisites first:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip build-essential clang lld cmake ninja-build pkg-config perl nasm yasm autoconf automake libtool make curl ca-certificates
```

Ensure PowerShell is available as `pwsh`, then create the isolated Conan environments from the repository root:

```bash
pwsh -File ./scripts/setup-conan-venvs.ps1
exec "$SHELL"
conan1 --version
conan2 --version
```

Configure Conan 1 profiles when you need a Linux baseline:

```bash
conan1 config init
conan1 config install ./settings
conan1 remote disable conancenter
```

The installed `linux-x86_64` Conan 1 profile records `compiler=clang` and `compiler.version=12` as the stable package setting, even when newer Clang binaries are used. CI installs LLVM through `Devolutions/actions-public/setup-llvm@v1` and currently requests LLVM `18.1.8`; local WSL iteration can use the distro `clang`/`clang++` pair from `apt`. If Git source downloads fail in WSL with `Unsupported SSL backend 'schannel'`, set the Linux Git backend explicitly:

```bash
git config --global http.sslBackend gnutls
```

## Conan 1 usage

Configure Conan 1 without touching Conan 2 state:

```powershell
conan1 config init
conan1 config install .\settings
conan1 remote disable conancenter
```

Build existing packages with the current PowerShell entry point:

```powershell
.\build.ps1 -Platform windows -Architecture x86_64 -BuildType Release
```

`build.ps1`, `publish.ps1`, and the Conan 1 workflows use `conan1` explicitly and read recipes from `conan1\recipes`.

## Conan 2 migration workflow

Conan 2 has parallel build coverage for the current Conan 1 package set across Windows, macOS, iOS, iOS simulator, Android, and Linux. Conan 1 remains the default workflow-dispatch and scheduled build path; Conan 2 can be selected with `conan_major_version=2` and also has its own scheduled validation lane. Manual package runs default to publish dry-runs with `publish_dry_run=true`; set it to `false` only when the resulting Artifactory upload is intended and approved.

The default local Conan 2 smoke-test lane is:

| Setting | Initial value |
| --- | --- |
| Platform | Windows |
| Architecture | x86_64 |
| Build type | Debug |
| Scope | Local cache validation with the Conan 2 recipe tree |

Migrate one package at a time:

```powershell
Copy-Item -Recurse .\conan1\recipes\zlib .\conan2\recipes\zlib
```

Port the copied recipe to Conan 2 APIs, then test it with `conan2` only:

```powershell
conan2 profile detect --force
.\scripts\test-conan2-recipe.ps1 zlib
```

Keep the Conan 1 recipe in `conan1\recipes` unchanged until the Conan 2 recipe is validated. Do not remove Conan 1 support as part of individual recipe migrations.

Before porting a recipe, build the original Conan 1 recipe on the same machine and target to establish a baseline:

```powershell
.\scripts\test-conan1-recipe.ps1 zlib
```

`scripts\test-conan2-recipe.ps1` defaults to `windows`, `x86_64`, and `Debug`. It also supports `x86`, `x64`/`x86_64`, `arm64`/`aarch64`, `Debug`, `Release`, and `RelWithDebInfo`. It runs `conan2 create` with the detected default Conan 2 profiles and `--build=missing` so each recipe can be iterated quickly from a normal local terminal.
On Windows, the helper uses Ninja and automatically enters the Visual Studio `vcvarsall.bat` compiler environment for the requested target architecture when `cl.exe` is not already on PATH.

### iOS simulator arm64 packages

Use `iossimulator` when building arm64 simulator packages. This keeps the existing `ios-arm64`/`ios-aarch64` device target unchanged while making the simulator SDK explicit.

Conan 1 uses checked-in profiles from `settings\profiles`; `iossimulator-arm64` is the primary profile and `iossimulator-aarch64` is an alias:

```powershell
conan1 config install .\settings
.\build.ps1 -Platform iossimulator -Architecture arm64 -BuildType Release
.\scripts\test-conan1-recipe.ps1 zlib -Platform iossimulator -Architecture arm64
```

Conan 2 derives the same target from script arguments and emits `os=iOS`, `arch=armv8`, and `os.sdk=iphonesimulator`:

```powershell
.\scripts\test-conan2-recipe.ps1 zlib -Platform iossimulator -Architecture arm64 -BuildType Debug
.\scripts\build-conan2.ps1 -Platform iossimulator -Architecture arm64 -BuildType Release
```

iOS simulator package builds require a macOS runner with Xcode.

### Linux x86_64 Debug iteration

The Linux migration lane starts with native WSL/Linux x86_64 Debug builds and keeps iteration package-by-package. Run the original Conan 1 recipe first when practical, then validate the Conan 2 recipe with Linux host settings and the Ninja generator:

```bash
./scripts/test-conan1-recipe.ps1 zlib -Platform linux -Architecture x86_64 -BuildType Debug
./scripts/test-conan2-recipe.ps1 zlib -Platform linux -Architecture x86_64 -BuildType Debug
```

The Conan 2 helper maps this to `os=Linux`, `arch=x86_64`, `build_type=Debug`, and `tools.cmake.cmaketoolchain:generator=Ninja`. Keep Windows validation on the existing default path by omitting `-Platform` or passing `-Platform windows`.

Validate Linux Debug in dependency/build order for fast feedback:

1. Prove the first small slice: `cbake`, `shared`, and `zlib`.
2. Continue with `cjson`, `libcbor`, `mbedtls`, `libressl`, `libpng`, `libjpeg`, and `libfido2`.
3. Validate `openh264` before `freerdp`; it is a Linux transitive requirement of the FreeRDP recipe.
4. Continue with `winpr`, `freerdp`, `pcre2`, `libvpx`, and `wxsqlite3`.

When a Linux failure reveals a missing dependency, distinguish host build tools from target libraries. Install missing host tools explicitly, but target Linux development headers and libraries should come from the Linux sysroot path rather than ad hoc host `-dev` packages.

The Conan 2 `sysroot` recipe defaults to CBake's prebuilt release archives, currently `v2026.01.15.0`, so local Linux validation does not require Docker just to populate the target sysroot. To force local CBake/Docker sysroot generation instead, pass Conan build-context option `-o:b sysroot/*:source=build`; the default prebuilt path is `-o:b sysroot/*:source=prebuilt`.

Validated locally on Linux x86_64 Debug with Conan 2 and the prebuilt sysroot: `cbake`, `sysroot`, `shared`, `webview`, `embedded-terminal`, `zlib`, `cjson`, `libcbor`, `mbedtls`, `libressl`, `libpng`, `libjpeg`, `libfido2`, `openh264`, `winpr`, `freerdp`, `pcre2`, `libudev-zero`, `libvpx`, and `wxsqlite3`.

### Initial migration order

The first Conan 2 slice follows the current `build.ps1` order for Windows x64 Debug:

1. Decide the Conan 2 shared helper strategy for `shared`: either keep a Conan 2 `python_requires` package or replace it with checked-in Python helper modules.
2. Port the first current-order slice: `cbake`, `shared`, `openh264`, `zlib`, and `cjson`.
3. Continue through the existing Windows x64 Debug order: `libpng`, `libjpeg`, `libcbor`, `mbedtls`, `libressl`, `libfido2`, `winpr`, `freerdp`, `pcre2`, `libvpx`, and `wxsqlite3`.
4. Linux-focused recipes such as `sysroot`, `webview`, `embedded-terminal`, and `libudev-zero` are part of the Conan 2 Linux/Android build order.

Use the Windows matrix as the local validation gate before moving on to macOS, Linux, Android, iOS, CI, and publishing.

Run the current first slice with:

```powershell
.\scripts\test-conan1-first-slice.ps1
.\scripts\test-conan2-first-slice.ps1
```

The first slice uses concrete Conan 2 references such as `cbake/0.2.3@devolutions/stable` because Conan 2 removed the Conan 1 `conan alias` command.

Run the current second slice with:

```powershell
.\scripts\test-conan1-second-slice.ps1 -ContinueOnError
.\scripts\test-conan2-second-slice.ps1
```

Current Windows x64 Debug Conan 2 coverage:

| Slice | Recipes | Conan 2 status | Conan 1 baseline note |
| --- | --- | --- | --- |
| First | `cbake`, `shared`, `openh264`, `zlib`, `cjson` | Builds; `zlib` and `cjson` test packages pass | `zlib` fails on this machine because Conan 1 hard-codes Visual Studio 2022 while only Visual Studio 2026 is installed |
| Second | `libpng`, `libjpeg`, `libcbor`, `mbedtls`, `libressl` | Builds; all test packages pass | `libpng` misses the Conan 1 `zlib` binary; the other CMake packages fail on the same Visual Studio 2022 generator issue |
| Third | `libfido2` | Builds; test package passes | Conan 1 stops before build because required local dependency binaries are missing |
| Fourth | `winpr`, `freerdp` | Builds; test packages pass | Conan 1 stops before build because `cjson/1.7.15` is missing and no remote is configured |
| Fifth | `pcre2`, `libvpx`, `wxsqlite3` | Builds; test packages pass | `pcre2` misses the Conan 1 `zlib` binary; `libvpx` and `wxsqlite3` fail on the Visual Studio 2022 generator issue |

The Windows x64 Debug lane is complete when all five slice runners pass in order:

```powershell
.\scripts\test-conan2-first-slice.ps1
.\scripts\test-conan2-second-slice.ps1
.\scripts\test-conan2-third-slice.ps1
.\scripts\test-conan2-fourth-slice.ps1
.\scripts\test-conan2-fifth-slice.ps1
```

Keep using the same baseline-first flow when expanding the matrix: run `scripts\test-conan1-recipe.ps1 <name>` first, record whether Conan 1 succeeds or fails on this machine, then port and validate with `scripts\test-conan2-recipe.ps1 <name>`. A Conan 1 failure caused by missing local binaries or the known Visual Studio 2022 generator mismatch is an environment baseline, not a Conan 2 regression.

### Windows Conan 2 matrix status

Run the current Windows Conan 2 matrix with:

```powershell
.\scripts\test-conan2-windows-matrix.ps1
```

The matrix has been validated locally with Conan 2 for Windows `x86`, `x86_64`, and `arm64` targets. It builds the full migrated package set for `Debug` and `Release`, and the same `RelWithDebInfo` subset used by `build.ps1`: `zlib`, `cjson`, `libpng`, `libjpeg`, `mbedtls`, `libressl`, `winpr`, `openh264`, `libcbor`, `libfido2`, and `freerdp`.
