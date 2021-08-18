from conans import ConanFile, tools, CMake, python_requires
import os

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class MinizConan(ConanFile):
    name = 'miniz'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    license = 'MIT'
    url = 'https://github.com/richgel999/miniz'
    description = 'miniz: Single C source file zlib-replacement library'
    settings = 'os', 'arch', 'build_type', 'compiler'

    options = {
        'fPIC': [True, False],
        'cmake_osx_architectures': 'ANY',
        'cmake_osx_deployment_target': 'ANY',
        'ios_deployment_target': 'ANY',
        'shared': [True, False]
    }

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.upstream_version))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.upstream_version)

    def build(self):
        if self.settings.arch == 'universal' and self.settings.os == 'iOS':
            lipo.create(self, self.build_folder)
            return

        cmake = CMake(self)
        utils.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['BUILD_EXAMPLES'] = 'OFF'
        cmake.definitions['BUILD_HEADER_ONLY'] = 'OFF'
        cmake.definitions['AMALGAMATE_SOURCES'] = 'ON'

        cmake.configure(source_folder=self.name)

        if self.settings.os == 'Windows':
            tools.replace_in_file('CMakeCache.txt', '/MD', '/MT', strict=False)
            cmake.configure(source_folder=self.name)

        cmake.build()

    def package(self):
        if self.settings.arch == 'universal':
            self.copy('*.a', dst='lib', keep_path=False)
            self.copy('*.h', src='include', dst='include')
            return

        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)

        self.copy('*.h', dst='include', keep_path=False) # CMAKE_BINARY_DIR

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
