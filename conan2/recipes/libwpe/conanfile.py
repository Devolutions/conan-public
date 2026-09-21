from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, load
import os


class LibwpeConan(ConanFile):
    name = "libwpe"
    exports = "VERSION"
    license = "BSD-2-Clause"
    url = "https://wpewebkit.org/releases"
    description = "General-purpose library for the WPE WebKit platform"
    settings = "os", "arch", "build_type"
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": True,
    }

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libwpe is only supported for Linux targets")
        if not self.options.shared:
            # WPE WebKit and WPEBackend-fdo both resolve libwpe at runtime through
            # wpe_loader_init(), which dlopens the backend implementation.
            raise ConanInvalidConfiguration("libwpe must be built shared")

    def layout(self):
        cmake_layout(self)

    def source(self):
        # Upstream publishes release tarballs; WebKit-family git histories are
        # many gigabytes, so cloning is not worth it for a pinned release.
        get(self, f"{self.url}/{self.name}-{self.version}.tar.xz", strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        # 1.16.0 still declares cmake_minimum_required(VERSION 3.0) and CMake 4.x
        # dropped compatibility below 3.5. A cache variable is required rather than
        # a plain one: the floor has to be raised before cmake_minimum_required runs.
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # Installed rather than hand-copied: the headers land under a versioned
        # include directory (include/wpe-1.0) and the SONAME symlinks matter to
        # anything that links libwpe by name.
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["wpe-1.0"]
        self.cpp_info.includedirs = [os.path.join("include", "wpe-1.0")]
