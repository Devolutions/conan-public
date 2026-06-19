from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, load
from conan.tools.scm import Git
import fileinput
import os
import sys


class LibpngConan(ConanFile):
    name = "libpng"
    exports = "VERSION"
    license = "PNG Reference Library License version 2"
    url = "https://github.com/glennrp/libpng.git"
    description = "Portable Network Graphics"
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

    def requirements(self):
        self.requires("zlib/1.3.1@devolutions/stable")

    def layout(self):
        cmake_layout(self)

    def source(self):
        folder = self.name
        tag = f"v{self.version}"
        self.output.info(f"Cloning repo: {self.url} dest: {folder} tag: {tag}")
        git = Git(self)
        git.clone(url=self.url, target=folder, args=["--branch", tag])

        cmake_lists = os.path.join(self.source_folder, folder, "CMakeLists.txt")
        for line in fileinput.input([cmake_lists], inplace=True):
            if line.strip().startswith("cmake_minimum_required"):
                line = "cmake_minimum_required(VERSION 3.6)\n"
            if line.strip().startswith("cmake_policy"):
                line = "cmake_policy(VERSION 3.6)\n"
            sys.stdout.write(line)

    def generate(self):
        zlib_path = self.dependencies["zlib"].package_folder.replace("\\", "/")
        zlib_library = "zlib.lib" if self.settings.os == "Windows" else "zlib.a"

        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["ENABLE_TESTING"] = False
        tc.variables["ENABLE_PROGRAMS"] = False
        tc.variables["PNG_STATIC"] = True
        tc.variables["PNG_SHARED"] = False
        tc.variables["PNG_FRAMEWORK"] = False
        tc.variables["PNG_TESTS"] = False
        tc.variables["ZLIB_ROOT_DIR"] = zlib_path
        tc.variables["ZLIB_BIN_DIRS"] = f"{zlib_path}/bin"
        tc.variables["ZLIB_INCLUDE_DIRS"] = f"{zlib_path}/include"
        tc.variables["ZLIB_LIBRARY_DIRS"] = f"{zlib_path}/lib"
        tc.variables["ZLIB_LIBRARY"] = f"{zlib_path}/lib/{zlib_library}"
        tc.variables["ZLIB_INCLUDE_DIR"] = f"{zlib_path}/include"
        if self.settings.os == "Windows":
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()

    def package(self):
        copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "png.h", src=os.path.join(self.source_folder, self.name), dst=os.path.join(self.package_folder, "include", "libpng16"), keep_path=False)
        copy(self, "pngconf.h", src=os.path.join(self.source_folder, self.name), dst=os.path.join(self.package_folder, "include", "libpng16"), keep_path=False)
        copy(self, "pnglibconf.h", src=self.build_folder, dst=os.path.join(self.package_folder, "include", "libpng16"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
