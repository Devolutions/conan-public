from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, load, patch
from conan.tools.scm import Git
import os


class LibreSSLConan(ConanFile):
    name = "libressl"
    exports = "VERSION", "patches/*"
    license = "BSD"
    url = "https://github.com/PowerShell/LibreSSL.git"
    description = "LibreSSL"
    settings = "os", "arch", "build_type"
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()

    def layout(self):
        cmake_layout(self)

    def source(self):
        folder = self.name
        tag = f"V{self.version}.0"
        self.output.info(f"Cloning repo: {self.url} dest: {folder} tag: {tag}")
        git = Git(self)
        git.clone(url=self.url, target=folder, args=["--branch", tag])

        patches_dir = os.path.join(self.recipe_folder, "patches", self.version)
        if os.path.isdir(patches_dir):
            for patch_file in sorted(os.listdir(patches_dir)):
                patch_path = os.path.join(patches_dir, patch_file)
                self.output.info(f"Applying patch: {patch_path}")
                patch(self, base_path=os.path.join(self.source_folder, folder), patch_file=patch_path)

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["USE_STATIC_MSVC_RUNTIMES"] = True
        tc.variables["CMAKE_INSTALL_LIBEXECDIR"] = "lib"
        tc.variables["CMAKE_SHARED_LIBRARY_PREFIX"] = "lib"
        tc.variables["CMAKE_STATIC_LIBRARY_PREFIX"] = "lib"
        tc.variables["LIBRESSL_APPS"] = self.settings.os != "iOS"
        tc.variables["LIBRESSL_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.buildenv_info.define_path("OPENSSL_DIR", self.package_folder)
        self.runenv_info.define_path("OPENSSL_DIR", self.package_folder)
