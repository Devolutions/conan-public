from conans import ConanFile, tools, python_requires, CMake
import os

class JpegConan(ConanFile):
    name = 'libjpeg'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Independent JPEG Group'
    url = 'https://github.com/wayk/libjpeg-turbo.git'
    description = 'libjpeg-turbo is a JPEG image codec that uses SIMD instructions to accelerate baseline JPEG compression and decompression'
    settings = 'os', 'arch', 'build_type'
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
        if self.settings.arch == 'universal':
            return

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url, branch=self.branch)

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

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

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        elif self.settings.arch == 'universal':
            self.copy('*.a', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib')

        if self.settings.arch == 'universal':
            self.copy('*.h', src='include', dst='include')
        else:
            for header in ['jpeglib.h', 'jerror.h', 'turbojpeg.h', 'jmorecfg.h']:
                self.copy(header, src=self.name, dst='include')

            self.copy('jconfig.h', dst='include')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
