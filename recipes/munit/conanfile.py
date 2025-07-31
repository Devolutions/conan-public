from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os, shutil

class MunitConan(ConanFile):
    name = 'munit'
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    license = 'Devolutions'
    url = 'https://github.com/nemequ/munit'
    description = 'µnit is a small testing framework for C'
    settings = 'os', 'arch', 'distro', 'build_type'
    tag = 'fbbdf14'
    python_requires = "shared/[1.0.0]@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    exports = ['VERSION',
        'patches/CMakeLists.txt']

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
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = Git(self, folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)

        patches_dir = os.path.join(self.recipe_folder, "patches")
        for file in ['CMakeLists.txt']:
            shutil.copy(os.path.join(patches_dir, file), os.path.join(folder, file))

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['ENABLE_TESTING'] = 'OFF'
        cmake.definitions['ENABLE_PROGRAMS'] = 'OFF'

        cmake.configure()

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            copy(self, '*.lib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        else:
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        copy(self, '*.h', src=os.path.join(self.source_folder, 'munit'), dst=os.path.join(self.package_folder, 'include'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
