from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, load, patch, rmdir
from conan.tools.scm import Git
import fileinput
import os
import sys


class JpegConan(ConanFile):
    name = "libjpeg"
    exports = "VERSION", "patches/*"
    license = "Independent JPEG Group"
    url = "https://github.com/libjpeg-turbo/libjpeg-turbo.git"
    description = "libjpeg-turbo is a JPEG image codec that uses SIMD instructions to accelerate baseline JPEG compression and decompression"
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
        tag = "aa829dc" if self.version == "2.1.0" else self.version
        self.output.info(f"Cloning repo: {self.url} dest: {folder} tag: {tag}")
        git = Git(self)
        git.clone(url=self.url, target=folder)
        Git(self, folder=folder).checkout(tag)

        patches_dir = os.path.join(self.recipe_folder, "patches", self.version)
        if os.path.isdir(patches_dir):
            for patch_file in sorted(os.listdir(patches_dir)):
                patch_path = os.path.join(patches_dir, patch_file)
                self.output.info(f"Applying patch: {patch_path}")
                patch(self, base_path=os.path.join(self.source_folder, folder), patch_file=patch_path)

        cmake_lists = os.path.join(self.source_folder, folder, "CMakeLists.txt")
        for line in fileinput.input([cmake_lists], inplace=True):
            if line.strip().startswith("cmake_minimum_required"):
                line = "cmake_minimum_required(VERSION 3.6)\n"
            sys.stdout.write(line)

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["CMAKE_INSTALL_INCLUDEDIR"] = "include"
        tc.variables["CMAKE_INSTALL_LIBDIR"] = "lib"
        tc.variables["CMAKE_INSTALL_BINDIR"] = "bin"
        tc.variables["CMAKE_INSTALL_SBINDIR"] = "bin"
        tc.variables["CMAKE_INSTALL_LIBEXECDIR"] = "bin"
        tc.variables["CMAKE_INSTALL_OLDINCLUDEDIR"] = "include"
        tc.variables["CMAKE_INSTALL_DATAROOTDIR"] = "share"
        tc.variables["ENABLE_SHARED"] = False
        tc.variables["ENABLE_STATIC"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()
        cmake.install()

    def package(self):
        for folder in ["bin", "share", os.path.join("lib", "cmake"), os.path.join("lib", "pkgconfig")]:
            rmdir(self, os.path.join(self.package_folder, folder))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
