from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, load, patch, replace_in_file
from conan.tools.scm import Git
import os


class LibFIDO2Conan(ConanFile):
    name = "libfido2"
    exports = "VERSION", "patches/*"
    license = "BSD"
    url = "https://github.com/PowerShell/libfido2"
    description = "libfido2"
    settings = "os", "arch", "build_type"
    no_copy_source = True
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

    def requirements(self):
        self.requires("zlib/1.3.1@devolutions/stable")
        self.requires("libcbor/0.10.2@devolutions/stable")
        self.requires("libressl/3.8.2@devolutions/stable")

        if self.settings.os == "Android":
            self.requires("libudev-zero/1.0.0@devolutions/stable")

    def layout(self):
        cmake_layout(self)

    def source(self):
        folder = self.name
        tag = self.version
        self.output.info(f"Cloning repo: {self.url} dest: {folder} tag: {tag}")
        git = Git(self)
        git.clone(url=self.url, target=folder, args=["--branch", tag])

        patches_dir = os.path.join(self.recipe_folder, "patches", self.version)
        if os.path.isdir(patches_dir):
            for patch_file in sorted(os.listdir(patches_dir)):
                patch_path = os.path.join(patches_dir, patch_file)
                self.output.info(f"Applying patch: {patch_path}")
                patch(self, base_path=os.path.join(self.source_folder, folder), patch_file=patch_path)

        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "CMakeLists.txt"),
            "cmake_minimum_required(VERSION 3.7)",
            "cmake_minimum_required(VERSION 3.15)",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "CMakeLists.txt"),
            "add_definitions(-DWIN32_LEAN_AND_MEAN -D_WIN32_WINNT=0x0600)",
            "add_definitions(-DWIN32_LEAN_AND_MEAN -D_WIN32_WINNT=0x0600)\nif(MSVC)\n\tadd_definitions(-D_CRT_SECURE_NO_WARNINGS -D_CRT_NONSTDC_NO_WARNINGS)\nendif()",
        )

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_TOOLS"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_MANPAGES"] = False
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["BUILD_STATIC_LIBS"] = not bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)

        if self.settings.os == "Windows":
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"

        zlib_path = self._cmake_path(self.dependencies["zlib"].package_folder)
        tc.variables["ZLIB_ROOT_DIR"] = zlib_path
        tc.variables["ZLIB_BIN_DIRS"] = f"{zlib_path}/bin"
        tc.variables["ZLIB_INCLUDE_DIRS"] = f"{zlib_path}/include"
        tc.variables["ZLIB_LIBRARY_DIRS"] = f"{zlib_path}/lib"

        libcbor_path = self._cmake_path(self.dependencies["libcbor"].package_folder)
        tc.variables["CBOR_ROOT_DIR"] = libcbor_path
        tc.variables["CBOR_BIN_DIRS"] = f"{libcbor_path}/bin"
        tc.variables["CBOR_INCLUDE_DIRS"] = f"{libcbor_path}/include"
        tc.variables["CBOR_LIBRARY_DIRS"] = f"{libcbor_path}/lib"

        libressl_path = self._cmake_path(self.dependencies["libressl"].package_folder)
        tc.variables["CRYPTO_ROOT_DIR"] = libressl_path
        tc.variables["CRYPTO_BIN_DIRS"] = f"{libressl_path}/bin"
        tc.variables["CRYPTO_INCLUDE_DIRS"] = f"{libressl_path}/include"
        tc.variables["CRYPTO_LIBRARY_DIRS"] = f"{libressl_path}/lib"

        if self.settings.os == "Android":
            tc.variables["UDEV_ROOT_DIR"] = self._cmake_path(self.dependencies["libudev-zero"].package_folder)

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.os == "Windows" and not self.options.shared:
            package_lib_dir = os.path.join(self.package_folder, "lib")
            static_lib = os.path.join(package_lib_dir, "fido2_static.lib")
            normalized_lib = os.path.join(package_lib_dir, "fido2.lib")
            if not os.path.isfile(static_lib) and not os.path.isfile(normalized_lib):
                raise RuntimeError(f"Missing expected static library: {static_lib}")
            if os.path.isfile(static_lib):
                if os.path.isfile(normalized_lib):
                    os.remove(normalized_lib)
                os.replace(static_lib, normalized_lib)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

    @staticmethod
    def _cmake_path(path):
        return path.replace("\\", "/")
