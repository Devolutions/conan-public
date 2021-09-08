from conans import ConanFile, tools, python_requires, CMake
import os

class MunitConan(ConanFile):
    name = 'munit'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Devolutions'
    url = 'https://github.com/Devolutions/munit.git'
    description = 'µnit is a small testing framework for C'
    settings = 'os', 'arch', 'distro', 'build_type'
    branch = 'wayk'
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

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
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url, self.branch)

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
