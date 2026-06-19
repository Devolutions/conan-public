from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import load, save
import os


class UtilsBase:
    def build_requirements(self):
        self.tool_requires("cbake/0.2.3@devolutions/stable")

        if self.get_target_os() == "Linux":
            self.tool_requires("sysroot/0.2.4@devolutions/stable")

    def get_target_os(self):
        try:
            return str(self.settings.os)
        except Exception:
            return None

    def get_target_arch(self):
        try:
            return str(self.settings.arch)
        except Exception:
            return None

    def apply_linux_sysroot(self, toolchain):
        if self.get_target_os() != "Linux":
            return

        sysroot = self._build_dependency("sysroot")
        cbake = self._build_dependency("cbake")
        sysroot_name = self._linux_sysroot_name(sysroot.package_folder)
        sysroot_path = os.path.join(sysroot.package_folder, sysroot_name).replace("\\", "/")
        cbake_toolchain = os.path.join(cbake.package_folder, "cmake", "linux.toolchain.cmake").replace("\\", "/")
        wrapper = os.path.join(self.generators_folder, "devolutions_linux_sysroot.cmake")

        save(
            self,
            wrapper,
            "\n".join(
                [
                    f'set(CMAKE_SYSROOT "{sysroot_path}" CACHE STRING "" FORCE)',
                    f'set(SYSROOT_NAME "{sysroot_name}" CACHE STRING "" FORCE)',
                    'if(NOT DEFINED LLVM_PREFIX AND DEFINED ENV{LLVM_PREFIX})',
                    '    set(LLVM_PREFIX "$ENV{LLVM_PREFIX}" CACHE PATH "" FORCE)',
                    'endif()',
                    'if(NOT DEFINED LLVM_PREFIX)',
                    '    foreach(_devolutions_llvm_prefix /usr/lib/llvm-18 /usr/lib/llvm-17 /usr/lib/llvm-16 /usr/lib/llvm-15 /usr/lib/llvm-14 /usr/lib/llvm-13 /usr/lib/llvm-12)',
                    '        if(EXISTS "${_devolutions_llvm_prefix}/bin/clang" AND EXISTS "${_devolutions_llvm_prefix}/bin/ld.lld")',
                    '            set(LLVM_PREFIX "${_devolutions_llvm_prefix}" CACHE PATH "" FORCE)',
                    '            break()',
                    '        endif()',
                    '    endforeach()',
                    'endif()',
                    f'include("{cbake_toolchain}")',
                    "",
                ]
            ),
        )

        user_toolchain_block = toolchain.blocks["user_toolchain"]
        values = user_toolchain_block.values or {"paths": []}
        paths = [wrapper.replace("\\", "/")] + list(values.get("paths") or [])
        user_toolchain_block.values = {"paths": paths}

    def _build_dependency(self, name):
        try:
            return self.dependencies.build[name]
        except Exception:
            return self.dependencies[name]

    @staticmethod
    def _linux_sysroot_name(package_folder):
        entries = [entry for entry in os.listdir(package_folder) if os.path.isdir(os.path.join(package_folder, entry))]
        if len(entries) != 1:
            raise RuntimeError(f"Expected exactly one sysroot directory in {package_folder}, found: {entries}")
        return entries[0]

    def openh264_filename(self, version):
        os_ = str(self.settings.os)
        arch = str(self.settings.arch)
        version = str(version)

        base_name = "libopenh264"
        ext = None
        platform = None

        if os_ == "Windows":
            base_name = "openh264"
            ext = "dll"
            if arch == "x86":
                platform = "win32"
            elif arch == "x86_64":
                platform = "win64"
            elif arch in ("armv8", "arm64"):
                platform = "win-arm64"
        elif os_ == "Linux":
            ext = "so"
            if arch == "x86_64":
                platform = "linux64.8"
            elif arch in ("armv8", "arm64"):
                platform = "linux-arm64.8"
        elif os_ == "Macos":
            ext = "dylib"
            if arch == "x86_64":
                platform = "mac-x64"
            elif arch in ("armv8", "arm64"):
                platform = "mac-arm64"

        if not platform or not ext:
            raise ConanInvalidConfiguration(f"Unsupported platform/arch: {os_} {arch}")

        return f"{base_name}-{version}-{platform}.{ext}"


class SharedUtils(ConanFile):
    name = "shared"
    exports = "VERSION"

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()
