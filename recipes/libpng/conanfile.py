from conan import ConanFile
from conan.tools.files import replace_in_file, copy, load, save
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os
import sys
import fileinput

class TemplateConan(ConanFile):
    name = 'libpng'
    exports_sources = "VERSION"
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    license = 'PNG Reference Library License version 2'
    url = 'https://github.com/glennrp/libpng.git'
    description = 'Portable Network Graphics'
    settings = 'os', 'arch', 'distro', 'build_type'
    tag = 'v%s' % version
    python_requires = "shared/[1.0.0]@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

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

    def build_requirements(self):
        super().build_requirements()
        self.tool_requires('zlib/[1.3.1]@devolutions/stable')

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = Git(self, folder=folder)
        git.clone(url=self.url, target=".")
        git.checkout(self.tag)

        if self.settings.os == 'Linux' and self.settings.arch == 'armv8':
            tools.replace_in_file(os.path.join(folder, 'CMakeLists.txt'),
            "arm/filter_neon.S",
            "#arm/filter_neon.S")

        # Modern Android NDK requires modern CMake policies
        for line in fileinput.input([os.path.join(folder, "CMakeLists.txt")], inplace=True):
            if line.strip().startswith('cmake_minimum_required'):
                line = 'cmake_minimum_required(VERSION 3.6)\n'
            if line.strip().startswith('cmake_policy'):
                line = 'cmake_policy(VERSION 3.6)\n'
            sys.stdout.write(line)

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['ENABLE_TESTING'] = 'OFF'
        cmake.definitions['ENABLE_PROGRAMS'] = 'OFF'
        cmake.definitions['PNG_SHARED'] = 'OFF'
        cmake.definitions['PNG_TESTS'] = 'OFF'

        zlib_path = self.dependencies['zlib'].package_folder
        cmake.definitions['ZLIB_ROOT_DIR'] = zlib_path
        cmake.definitions['ZLIB_BIN_DIRS'] = os.path.join(zlib_path, 'bin')
        cmake.definitions['ZLIB_INCLUDE_DIRS'] = os.path.join(zlib_path, 'include')
        cmake.definitions['ZLIB_LIBRARY_DIRS'] = os.path.join(zlib_path, 'lib')

        if self.settings.os == 'Linux':
            cmake.definitions['CMAKE_C_FLAGS_INIT'] = '-fPIC'

        if self.settings.os == 'Windows':
            cmake.definitions['ZLIB_LIBRARY'] = os.path.join(self.dependencies['zlib'].package_folder, 'lib', 'zlibstatic.lib')
        else:
            cmake.definitions['ZLIB_LIBRARY'] = os.path.join(self.dependencies['zlib'].package_folder, 'lib', 'zlib.a')

        cmake.definitions['ZLIB_INCLUDE_DIR'] = os.path.join(self.dependencies['zlib'].package_folder, 'include')

        cmake.configure()

        if self.settings.os == "Windows":
            tools.replace_in_file("CMakeCache.txt", '/MD', '/MT', strict = False)
            cmake.configure()

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            copy(self, '*.lib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        elif self.settings.arch == 'universal':
            copy(self, '*.a')
        else:
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib', dst=self.package_folder, src=self.build_folder), src=self.build_folder)

        if self.settings.arch == 'universal':
            copy(self, '*.h', dst=self.package_folder, src=self.build_folder)
        else:
            for header in ['png.h', 'pngconf.h']:
                copy(self, header, src=os.path.join(self.source_folder, 'libpng'), dst=os.path.join(self.package_folder, 'include/libpng16'))
            copy(self, 'pnglibconf.h', dst=os.path.join(self.package_folder, 'include/libpng16'), src=self.build_folder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
