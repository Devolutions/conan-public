from conans import ConanFile, tools, CMake, python_requires
import os

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class CurlConan(ConanFile):
    name = 'curl'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Curl'
    url = 'https://github.com/Devolutions/curl.git'
    description = 'An open source, portable, easy to use, readable and flexible SSL library'
    settings = 'os', 'arch', 'build_type'
    branch = 'curl-%s-patched' % (version)

    options = {
        'fPIC': [True, False],
        'shared': [True, False]
    }
    default_options = {
        'fPIC': True,
        'shared': False
    }

    def build_requirements(self):
        self.build_requires('mbedtls/2.16.0@devolutions/stable')

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url, self.branch)

    def build(self):
        if self.settings.arch == 'universal':
            lipo.create(self, self.build_folder)
            return

        cmake = CMake(self)
        utils.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['CMAKE_USE_MBEDTLS'] = 'ON'
        cmake.definitions['CMAKE_USE_LIBSSH2'] = 'OFF'
        cmake.definitions['CURL_STATICLIB'] = 'ON'
        cmake.definitions['BUILD_TESTING'] = 'OFF'
        cmake.definitions['ENABLE_MANUAL'] = 'OFF'
        cmake.definitions['ENABLE_CURL_CONFIG'] = 'OFF'
        cmake.definitions['HTTP_ONLY'] = 'ON'
        cmake.definitions['BUILD_CURL_EXE'] = 'OFF'

        if self.settings.os == 'Windows':
            cmake.definitions['CURL_STATIC_CRT'] = 'ON'

        cmake.definitions['CMAKE_PREFIX_PATH'] = os.path.join(self.deps_cpp_info['mbedtls'].rootpath)

        cmake.configure(source_folder=self.name)

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)
        self.copy('*.h', src='curl/include/curl', dst='include/curl', keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == 'Windows':
            for flag in ['ncrypt']:
                self.cpp_info.libs.append(flag)
