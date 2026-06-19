from conan import ConanFile
from conan.tools.files import copy, download, get, load, mkdir, rmdir
import os


class SysrootConan(ConanFile):
    name = "sysroot"
    exports = "VERSION"
    license = "MIT"
    url = "https://github.com/Devolutions/CBake.git"
    description = "Linux sysroot"
    settings = "os", "arch"
    options = {
        "distro": [
            "alpine-3.14",
            "alpine-3.17",
            "alpine-3.21",
            "debian-10",
            "debian-11",
            "debian-12",
            "opensuse-15.2",
            "rhel8",
            "rhel9",
            "ubuntu-18.04",
            "ubuntu-20.04",
            "ubuntu-22.04",
            "ubuntu-24.04",
        ],
        "source": ["prebuilt", "build"],
        "release": ["ANY"],
        "target_arch": ["auto", "x86_64", "x64", "armv8", "arm64", "aarch64"],
    }
    default_options = {
        "distro": "ubuntu-20.04",
        "source": "prebuilt",
        "release": "v2026.01.15.0",
        "target_arch": "auto",
    }

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()

    def build_requirements(self):
        if self.options.source == "build":
            self.tool_requires("cbake/0.2.3@devolutions/stable")

    def build(self):
        if self.options.source == "prebuilt":
            self._download_prebuilt_sysroot()
        else:
            self._build_sysroot()

        self._validate_sysroot(os.path.join(self.build_folder, self._sysroot_name()))

    def package(self):
        sysroot_name = self._sysroot_name()
        sysroot_dir = os.path.join(self.build_folder, sysroot_name)
        self._validate_sysroot(sysroot_dir)
        copy(self, "*", src=sysroot_dir, dst=os.path.join(self.package_folder, sysroot_name))

    def package_info(self):
        sysroot_name = self._sysroot_name()
        sysroot_path = os.path.join(self.package_folder, sysroot_name)
        self.buildenv_info.define_path("CMAKE_SYSROOT", sysroot_path)
        self.buildenv_info.define("SYSROOT_NAME", sysroot_name)
        self.runenv_info.define_path("CMAKE_SYSROOT", sysroot_path)
        self.runenv_info.define("SYSROOT_NAME", sysroot_name)
        self.conf_info.define("tools.build:sysroot", sysroot_path)

    def _download_prebuilt_sysroot(self):
        sysroot_name = self._sysroot_name()
        filename = f"{sysroot_name}-sysroot.tar.xz"
        release_url = self._release_url()
        checksums_path = os.path.join(self.build_folder, "checksums")

        download(self, f"{release_url}/checksums", checksums_path)
        sha256 = self._checksum_for(checksums_path, filename)
        rmdir(self, os.path.join(self.build_folder, sysroot_name))
        get(self, url=f"{release_url}/{filename}", destination=self.build_folder, sha256=sha256, strip_root=False)

    def _build_sysroot(self):
        cbake_home = self.dependencies.build["cbake"].package_folder
        build_script = os.path.join(cbake_home, "build.ps1")
        export_dir = os.path.join(self.build_folder, self._sysroot_name())
        mkdir(self, export_dir)

        self.run(
            f'pwsh -File "{build_script}" sysroot '
            f'-Distribution "{self.options.distro}" '
            f'-Architecture "{self._sysroot_arch()}" '
            f'-ExportPath "{export_dir}" '
            '-SkipPackaging'
        )

    def _release_url(self):
        return f"https://github.com/Devolutions/CBake/releases/download/{self.options.release}"

    @staticmethod
    def _checksum_for(checksums_path, filename):
        with open(checksums_path, "r", encoding="utf-8") as checksums:
            for line in checksums:
                parts = line.strip().split()
                if len(parts) == 2 and parts[1] == filename:
                    return parts[0].lower()

        raise RuntimeError(f"No checksum found for {filename} in {checksums_path}")

    def _sysroot_name(self):
        return f"{self.options.distro}-{self._sysroot_arch()}"

    def _sysroot_arch(self):
        arch = str(self.options.target_arch)
        if arch == "auto":
            arch = str(self.settings.arch)

        return {
            "x86_64": "amd64",
            "x64": "amd64",
            "armv8": "arm64",
            "arm64": "arm64",
            "aarch64": "arm64",
        }[arch]

    @staticmethod
    def _validate_sysroot(path):
        usr_dir = os.path.join(path, "usr")
        if not os.path.isdir(usr_dir):
            raise RuntimeError(f"Sysroot was not generated correctly; missing expected directory: {usr_dir}")
