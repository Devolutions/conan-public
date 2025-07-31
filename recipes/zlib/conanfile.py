from conan import ConanFile
from conans import tools  # Keep for compatibility
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.scm import Git
from conan.tools.files import load, replace_in_file, copy
import os

class ZlibConan(ConanFile):
    name = 'zlib'
    license = 'Zlib'
    url = 'https://github.com/madler/zlib.git'
    description = 'zlib is a general purpose data compression library.'
    settings = 'os', 'arch', 'distro', 'build_type'
    python_requires = "shared/[1.0.0]@devolutions/stable"
    
    def set_version(self):
        version_path = os.path.join(os.path.dirname(__file__), 'VERSION')
        with open(version_path, 'r') as f:
            self.version = f.read().strip()
            self.tag = 'v' + self.version
    python_requires_extend = "shared.UtilsBase"
    exports_sources = "VERSION"

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
        if self.settings.arch == 'universal':
            return

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = Git(self, folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)

        if self.settings.os == 'Windows':
            replace_in_file(self, os.path.join(folder, 'CMakeLists.txt'),
                "set(CMAKE_DEBUG_POSTFIX \"d\")",
                "set(CMAKE_DEBUG_POSTFIX \"\")")

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        cmake.configure()

        if self.settings.os == 'Windows':
            replace_in_file(self, os.path.join(self.build_folder, 'CMakeCache.txt'), '/MD', '/MT')
            cmake.configure()

        args = ['--target', 'zlibstatic'] if self.settings.os == 'iOS' else None
        cmake.build(args=args)

    def package(self):
        if self.settings.arch == 'universal':
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
            copy(self, '*.h', src=os.path.join(self.build_folder, 'include'), dst=os.path.join(self.package_folder, 'include'))
            return

        if self.settings.os == 'Windows':
            copy(self, '*.lib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder, keep_path=False)
            lib_folder = os.path.join(self.package_folder, 'lib')
            zlib_lib = os.path.join(lib_folder, 'zlib.lib')
            zlibstatic_lib = os.path.join(lib_folder, 'zlibstatic.lib')
            if os.path.exists(zlib_lib):
                os.remove(zlib_lib)
            if os.path.exists(zlibstatic_lib):
                os.rename(zlibstatic_lib, zlib_lib)
        else:
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)

        copy(self, 'zconf.h', dst=os.path.join(self.package_folder, 'include'), src=self.build_folder)
        copy(self, 'zlib.h', src=os.path.join(self.source_folder, 'zlib'), dst=os.path.join(self.package_folder, 'include'))

    def package_info(self):
        if self.settings.os == 'Windows':
            self.cpp_info.libs = ['zlib']
        else:
            self.cpp_info.libs = ['z']
