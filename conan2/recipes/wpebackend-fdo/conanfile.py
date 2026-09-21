from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import PkgConfigDeps
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.files import get, load
from conan.tools.layout import basic_layout
import os


class WpeBackendFdoConan(ConanFile):
    name = "wpebackend-fdo"
    exports = "VERSION"
    license = "BSD-2-Clause"
    url = "https://wpewebkit.org/releases"
    description = "freedesktop.org backend for WPE WebKit"
    settings = "os", "arch", "build_type"
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": True,
    }

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("wpebackend-fdo is only supported for Linux targets")
        if not self.options.shared:
            # wpe_loader_init() dlopens this by soname; a static build is unusable.
            raise ConanInvalidConfiguration("wpebackend-fdo must be built shared")

    def requirements(self):
        self.requires("libwpe/1.16.0@devolutions/stable")

    def build_requirements(self):
        super().build_requirements()
        # The only Meson project in this repository, hence the extra tool.
        self.tool_requires("meson/[>=1.2]")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, f"{self.url}/{self.name}-{self.version}.tar.xz", strip_root=True)

    def generate(self):
        # libwpe is consumed through pkg-config (meson.build does dependency('wpe-1.0')),
        # so the Conan package has to be exposed as a .pc file rather than as CMake config.
        PkgConfigDeps(self).generate()

        tc = MesonToolchain(self)
        self._apply_linux_sysroot(tc)
        tc.generate()

    # UtilsBase.apply_linux_sysroot() only knows how to patch a CMakeToolchain: it writes a
    # CMake wrapper and injects it into the toolchain's user_toolchain block. Meson takes the
    # sysroot as ordinary compiler and linker flags instead, so the same resolution is redone
    # here. Worth lifting into shared.UtilsBase if a second Meson recipe ever lands.
    def _apply_linux_sysroot(self, toolchain):
        if self.get_target_os() != "Linux":
            return

        sysroot = self._build_dependency("sysroot")
        sysroot_name = self._linux_sysroot_name(sysroot.package_folder)
        sysroot_path = os.path.join(sysroot.package_folder, sysroot_name).replace("\\", "/")
        flag = f"--sysroot={sysroot_path}"

        for args in (toolchain.c_args, toolchain.cpp_args, toolchain.c_link_args, toolchain.cpp_link_args):
            args.append(flag)

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()

    def package_info(self):
        self.cpp_info.libs = ["WPEBackend-fdo-1.0"]
        self.cpp_info.includedirs = [os.path.join("include", "wpe-fdo-1.0")]
