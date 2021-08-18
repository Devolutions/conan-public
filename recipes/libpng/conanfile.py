from conans import ConanFile, CMake, tools, python_requires
import os

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class TemplateConan(ConanFile):
    name = 'libpng'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    license = 'PNG Reference Library License version 2'
    url = 'https://github.com/glennrp/libpng.git'
    description = 'Portable Network Graphics'
    settings = 'os', 'arch', 'build_type', 'compiler'
    tag = 'v%s' % upstream_version

    options = {
        'fPIC': [True, False],
        'cmake_osx_architectures': 'ANY',
        'cmake_osx_deployment_target': 'ANY',
        'ios_deployment_target': 'ANY',
        'shared': [True, False]
    }

    def build_requirements(self):
        self.build_requires('zlib/1.2.11-5@devolutions/stable')

    def source(self):
        if self.settings.arch != 'universal':
            folder = self.name

            self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
            git = tools.Git(folder=folder)
            git.clone(self.url)
            git.checkout(self.tag)

    def build(self):
        if self.settings.arch == 'universal' and self.settings.os == 'iOS':
            lipo.create(self, self.build_folder)
        else:
            cmake = CMake(self)
            utils.cmake_wrapper(cmake, self.settings, self.options)

            cmake.definitions['ENABLE_TESTING'] = 'OFF'
            cmake.definitions['ENABLE_PROGRAMS'] = 'OFF'
            cmake.definitions['PNG_SHARED'] = 'OFF'
            cmake.definitions['PNG_TESTS'] = 'OFF'

            if self.settings.os == 'Linux':
                cmake.definitions['CMAKE_C_FLAGS_INIT'] = '-fPIC'
            elif self.settings.os == 'Windows':
                cmake.definitions['ZLIB_LIBRARY'] = os.path.join(self.deps_cpp_info['zlib'].rootpath, 'lib', 'zlibstatic.lib')
                cmake.definitions['ZLIB_INCLUDE_DIR'] = os.path.join(self.deps_cpp_info['zlib'].rootpath, 'include')

            cmake.configure(source_folder=self.name)

            # conan doesn't support properly switching runtimes at the moment,
            # need to use this hack in the meantime
            if self.settings.os == 'Windows':
                tools.replace_in_file('CMakeCache.txt', '/MD', '/MT', strict=False)
                cmake.configure(source_folder=self.name)

            cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        elif self.settings.os == 'iOS' and self.settings.arch == 'universal':
            self.copy('*.a')
        else:
            self.copy('*.a', dst='lib')

        if self.settings.os == 'iOS' and self.settings.arch == 'universal':
            self.copy('*.h')
        else:
            for header in ['png.h', 'pngconf.h']:
                self.copy(header, src='libpng', dst='include/libpng16')
            self.copy('pnglibconf.h', dst='include/libpng16')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
