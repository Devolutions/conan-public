from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, load, patch, replace_in_file
import os


class PCREConan(ConanFile):
    name = "pcre2"
    exports = "VERSION"
    url = "https://github.com/bincrafters/conan-pcre2"
    description = "Perl Compatible Regular Expressions"
    homepage = "https://www.pcre.org/"
    license = "BSD-3-Clause"
    exports_sources = "CMakeLists.txt", "ios-clear_cache.patch", "jit_aarch64.patch"
    settings = "os", "arch", "build_type"
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "build_pcre2_8": [True, False],
        "build_pcre2_16": [True, False],
        "build_pcre2_32": [True, False],
        "support_jit": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "build_pcre2_8": True,
        "build_pcre2_16": True,
        "build_pcre2_32": True,
        "support_jit": True,
    }

    _source_subfolder = "source_subfolder"

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()

    def requirements(self):
        self.requires("zlib/1.3.1@devolutions/stable")

    def layout(self):
        cmake_layout(self)

    def source(self):
        source_url = f"https://github.com/PhilipHazel/pcre2/archive/refs/tags/pcre2-{self.version}.tar.gz"
        get(self, url=source_url, destination=os.path.join(self.source_folder, self._source_subfolder), strip_root=True)

        patch(self, patch_file=os.path.join(self.export_sources_folder, "ios-clear_cache.patch"), base_path=os.path.join(self.source_folder, self._source_subfolder, "src"))
        replace_in_file(
            self,
            os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"),
            "CMAKE_MINIMUM_REQUIRED(VERSION 2.8.0)",
            "CMAKE_MINIMUM_REQUIRED(VERSION 3.6)",
        )

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["PCRE2_BUILD_TESTS"] = False
        tc.variables["PCRE2_DEBUG"] = self.settings.build_type == "Debug"
        tc.variables["PCRE2_BUILD_PCRE2_8"] = bool(self.options.build_pcre2_8)
        tc.variables["PCRE2_BUILD_PCRE2_16"] = bool(self.options.build_pcre2_16)
        tc.variables["PCRE2_BUILD_PCRE2_32"] = bool(self.options.build_pcre2_32)
        tc.variables["PCRE2_SUPPORT_JIT"] = bool(self.options.support_jit)
        tc.variables["PCRE2_BUILD_PCRE2GREP"] = False

        if self.settings.os == "Windows":
            tc.variables["PCRE2_STATIC_RUNTIME"] = True
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self._source_subfolder))
        cmake.build()

    def package(self):
        if self.settings.os == "Windows":
            copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        else:
            copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

        copy(self, "*pcre2posix.h", src=os.path.join(self.source_folder, self._source_subfolder), dst=os.path.join(self.package_folder, "include"), keep_path=False)
        copy(self, "*pcre2.h", src=self.build_folder, dst=os.path.join(self.package_folder, "include"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
