from conans import ConanFile, CMake, tools, python_requires
import os

class MbedtlsConan(ConanFile):
    name = 'mbedtls'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Apache 2.0'
    url = 'https://github.com/Devolutions/mbedtls.git'
    description = 'An open source, portable, easy to use, readable and flexible SSL library'
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
        if self.settings.arch == 'universal':
            return

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

        if self.settings.os == 'Windows':
            cmake.definitions['MSVC_RUNTIME'] = 'static'

        mbedtls_configs = ['MBEDTLS_THREADING_C', 'MBEDTLS_HAVEGE_C', 'MBEDTLS_MD4_C', 'MBEDTLS_CMAC_C', 'MBEDTLS_RSA_C']
        if self.settings.os == 'Windows':
            mbedtls_configs.extend(['MBEDTLS_THREADING_WINDOWS'])
        else:
            mbedtls_configs.extend(['MBEDTLS_THREADING_PTHREAD'])

        config_h = os.path.join(self.source_folder, 'mbedtls', 'include', 'mbedtls', 'config.h')

        for config in mbedtls_configs:
            config_string = '#define %s' % config
            tools.replace_in_file(config_h, '//%s' % config_string, config_string)

        cmake.configure(source_folder=self.name)

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)
        self.copy('*.h', src='include', dst='include')

    def package_info(self):
        self.cpp_info.libs = ['mbedtls', 'mbedx509', 'mbedcrypto']
