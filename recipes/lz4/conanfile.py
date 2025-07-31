from conan import ConanFile
from conans import tools  # Keep for compatibility
from conan.tools.files import replace_in_file, copy, load, save
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os

class Lz4Conan(ConanFile):
    name = 'lz4'
    exports_sources = "VERSION"
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    license = 'BSD'
    url = 'https://github.com/lz4/lz4.git'
    description = 'Description'
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

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = Git(self, folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return
        
        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        cmake.configure())

        if self.settings.os == "Windows":
            tools.replace_in_file("CMakeCache.txt", '/MD', '/MT', strict = False)
            cmake.configure())

        cmake.build(args=['--target', 'lz4_static'])

    def package(self):
        if self.settings.os == 'Windows':
            copy(self, '*.lib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        elif self.settings.arch == 'universal':
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        else:
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)

        for header in ['lz4.h', 'lz4frame.h', 'lz4hc.h']:
            copy(self, header, src=os.path.join(self.source_folder, 'lz4/lib'), dst=os.path.join(self.package_folder, 'include'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
