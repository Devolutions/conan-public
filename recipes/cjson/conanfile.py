from conan import ConanFile
from conans import tools  # Keep for compatibility
from conan.tools.files import replace_in_file, copy, load, save
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os
import sys
import fileinput

class CjsonConan(ConanFile):
    name = 'cjson'
    exports_sources = "VERSION"
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    license = 'MIT'
    url = 'https://github.com/DaveGamble/cJSON'
    description = 'cJSON: Ultralightweight JSON parser in ANSI C'
    settings = 'os', 'arch', 'distro', 'build_type'
    no_copy_source = True
    branch = 'v' + version
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

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.branch))
        git = Git(self, folder=folder)
        git.clone(self.url)
        git.checkout(self.branch)

        # Modern Android NDK requires modern CMake policies
        for line in fileinput.input([os.path.join(folder, "CMakeLists.txt")], inplace=True):
            if line.strip().startswith('cmake_minimum_required'):
                line = 'cmake_minimum_required(VERSION 3.6)\n'
            sys.stdout.write(line)

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['BUILD_SHARED_LIBS'] = 'OFF'
        cmake.definitions['ENABLE_CJSON_TEST'] = 'OFF'
        cmake.definitions['ENABLE_LOCALES'] = 'OFF'
        cmake.definitions['ENABLE_TARGET_EXPORT'] = 'OFF'
        cmake.definitions['ENABLE_CJSON_UNINSTALL'] = 'OFF'

        cmake.configure()

        if self.settings.os == "Windows":
            tools.replace_in_file("CMakeCache.txt", '/MD', '/MT', strict = False)
            cmake.configure()

        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.arch == 'universal':
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
            copy(self, '*.h', src=os.path.join(self.source_folder, 'include'), dst=os.path.join(self.package_folder, 'include'))
            return

        if self.settings.os == 'Windows':
            copy(self, '*.lib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        else:
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)

        copy(self, '*.h', dst=os.path.join(self.package_folder, 'include'), src=self.build_folder) # CMAKE_BINARY_DIR

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
