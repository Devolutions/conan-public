from conans import ConanFile, tools, python_requires, CMake
import os, shutil

class MunitConan(ConanFile):
    name = 'munit'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Devolutions'
    url = 'https://github.com/nemequ/munit'
    description = 'µnit is a small testing framework for C'
    settings = 'os', 'arch', 'distro', 'build_type'
    tag = 'fbbdf14'
    python_requires = "shared/1.0.0@devolutions/stable"
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

    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = tools.Git(folder=folder)
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

        cmake.configure(source_folder=self.name)

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)
        self.copy('*.h', src='munit', dst='include')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
