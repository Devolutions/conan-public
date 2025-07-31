from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os
import sys
import fileinput

class JpegConan(ConanFile):
    name = 'libjpeg'
    exports_sources = "VERSION"
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    license = 'Independent JPEG Group'
    url = 'https://github.com/libjpeg-turbo/libjpeg-turbo.git'
    description = 'libjpeg-turbo is a JPEG image codec that uses SIMD instructions to accelerate baseline JPEG compression and decompression'
    settings = 'os', 'arch', 'distro', 'build_type'
    python_requires = "shared/[1.0.0]@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    exports = ['VERSION',
        'patches/2.1.0/0001-cmake-build-fixes.patch',
        'patches/2.1.5.1/0001-cmake-build-fixes.patch',
        'patches/3.1.0/0001-cmake-build-fixes.patch']

    options = {
        'fPIC': [True, False],
        'shared': [True, False]
    }
    default_options = {
        'fPIC': True,
        'shared': False
    }

    def layout(self):
        cmake_layout(self)

    def source(self):
        folder = self.name
        tag = self.version
        if tag == "2.1.0":
            tag = 'aa829dc' # we pinned this commit a while back even if it's not 2.1.0
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, tag))
        git = Git(self, folder=folder)
        git.clone(url=self.url, target=".")
        git.checkout(tag)

        git = Git(self, folder=folder)
        patches_dir = os.path.join(self.recipe_folder, "patches", self.version)
        if os.path.isdir(patches_dir):
            for patch_file in os.listdir(patches_dir):
                patch_path = os.path.join(patches_dir, patch_file)
                self.output.info('Applying patch: %s' % patch_path)
                git.run('apply --whitespace=nowarn %s' % (patch_path))

        # Modern Android NDK requires modern CMake policies
        for line in fileinput.input([os.path.join(folder, "CMakeLists.txt")], inplace=True):
            if line.strip().startswith('cmake_minimum_required'):
                line = 'cmake_minimum_required(VERSION 3.6)\n'
            sys.stdout.write(line)

    def build(self):
        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions["CMAKE_INSTALL_INCLUDEDIR:PATH"] = "include"
        cmake.definitions["CMAKE_INSTALL_LIBDIR:PATH"] = "lib"
        cmake.definitions["CMAKE_INSTALL_BINDIR:PATH"] = "bin"
        cmake.definitions["CMAKE_INSTALL_DATAROOTDIR:PATH"] = "share"

        cmake.definitions['ENABLE_SHARED'] = 'OFF'
        cmake.definitions['ENABLE_STATIC'] = 'ON'

        if self.settings.os == 'Windows' and self.settings.arch == 'armv8':
            cmake.definitions['CMAKE_SYSTEM_PROCESSOR'] = 'aarch64'
            cmake.definitions['WITH_SIMD'] = 'OFF'
        elif self.settings.os == 'Macos' and self.settings.arch == 'armv8':
            cmake.definitions['CMAKE_SYSTEM_PROCESSOR'] = 'aarch64'
            cmake.definitions['WITH_SIMD'] = 'OFF'

        cmake.configure()

        cmake.build()
        cmake.install()

    def package(self):
        for folder in ["bin", "share", "lib/cmake", "lib/pkgconfig"]:
            folder_path = os.path.join(self.package_folder, folder)
            if os.path.exists(folder_path):
                tools.rmdir(folder_path)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
