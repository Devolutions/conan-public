from conans import ConanFile, tools, python_requires, CMake
import os

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class JpegConan(ConanFile):
    name = 'libjpeg-turbo'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    license = 'Independent JPEG Group'
    url = 'https://github.com/wayk/libjpeg-turbo.git'
    description = 'libjpeg-turbo is a JPEG image codec that uses SIMD instructions to accelerate baseline JPEG compression and decompression'
    settings = 'os', 'arch', 'build_type', 'compiler'
    branch = 'wayk'

    options = {
        'fPIC': [True, False],
        'cmake_osx_architectures': 'ANY',
        'cmake_osx_deployment_target': 'ANY',
        'ios_deployment_target': 'ANY',
        'shared': [True, False]
    }

    def source(self):
        if self.settings.arch != 'universal':
            folder = self.name

            self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
            git = tools.Git(folder=folder)
            git.clone(self.url, branch=self.branch)

    def build(self):
        if self.settings.arch == 'universal' and self.settings.os == 'iOS':
            lipo.create(self, self.build_folder)
        else:
            cmake = CMake(self)
            utils.cmake_wrapper(cmake, self.settings, self.options)

            cmake.definitions['ENABLE_TESTING'] = 'OFF'
            cmake.definitions['ENABLE_SHARED'] = 'OFF'
            cmake.definitions['ENABLE_STATIC'] = 'ON'

            if self.settings.os == 'Windows' and self.settings.arch == 'armv8':
                cmake.definitions['CMAKE_SYSTEM_PROCESSOR'] = 'aarch64'
                cmake.definitions['WITH_SIMD'] = 'OFF'
            elif self.settings.os == 'Macos' and self.settings.arch == 'armv8':
                cmake.definitions['CMAKE_SYSTEM_PROCESSOR'] = 'aarch64'
                cmake.definitions['WITH_SIMD'] = 'OFF'

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
            self.copy('*.a', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib')

        if self.settings.os == 'iOS' and self.settings.arch == 'universal':
            self.copy('*.h', src='include', dst='include')
        else:
            for header in ['jpeglib.h', 'jerror.h', 'turbojpeg.h', 'jmorecfg.h']:
                self.copy(header, src=self.name, dst='include')

            self.copy('jconfig.h', dst='include')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
