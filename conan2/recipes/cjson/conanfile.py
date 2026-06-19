from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import load
from conan.tools.scm import Git
import fileinput
import os
import sys


class CjsonConan(ConanFile):
    name = "cjson"
    exports = "VERSION"
    license = "MIT"
    url = "https://github.com/DaveGamble/cJSON"
    description = "cJSON: Ultralightweight JSON parser in ANSI C"
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

    def layout(self):
        cmake_layout(self)

    def source(self):
        folder = self.name
        branch = f"v{self.version}"
        self.output.info(f"Cloning repo: {self.url} dest: {folder} tag: {branch}")
        git = Git(self)
        git.clone(url=self.url, target=folder, args=["--branch", branch])

        cmake_lists = os.path.join(self.source_folder, folder, "CMakeLists.txt")
        for line in fileinput.input([cmake_lists], inplace=True):
            if line.strip().startswith("cmake_minimum_required"):
                line = "cmake_minimum_required(VERSION 3.6)\n"
            sys.stdout.write(line)

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = False
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["ENABLE_CJSON_TEST"] = False
        tc.variables["ENABLE_LOCALES"] = False
        tc.variables["ENABLE_TARGET_EXPORT"] = False
        tc.variables["ENABLE_CJSON_UNINSTALL"] = False
        if self.settings.os == "Windows":
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["cjson"]
