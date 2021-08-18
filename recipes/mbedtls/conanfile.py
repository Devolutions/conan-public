from conans import ConanFile, CMake, tools, python_requires
import os

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class MbedtlsConan(ConanFile):
    name = 'mbedtls'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    license = 'Apache 2.0'
    url = 'https://github.com/Devolutions/mbedtls.git'
    description = 'An open source, portable, easy to use, readable and flexible SSL library'
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
            git.clone(self.url, self.branch)

    def build(self):
        if self.settings.arch == 'universal':
            lipo.create(self, self.build_folder)
        else:
            cmake = CMake(self)
            utils.cmake_wrapper(cmake, self.settings, self.options)

            cmake.definitions['ENABLE_TESTING'] = 'OFF'
            cmake.definitions['ENABLE_PROGRAMS'] = 'OFF'

            if self.settings.os == 'Windows':
                cmake.definitions['MSVC_RUNTIME'] = 'static'

            mbedtls_configs = ['MBEDTLS_THREADING_C', 'MBEDTLS_HAVEGE_C', 'MBEDTLS_MD4_C']
            if self.settings.os == 'Windows':
                mbedtls_configs.extend(['MBEDTLS_THREADING_WINDOWS'])
            else:
                mbedtls_configs.extend(['MBEDTLS_THREADING_PTHREAD'])

            config_h = os.path.join(self.source_folder, 'mbedtls', 'include', 'mbedtls', 'config.h')

            for config in mbedtls_configs:
                config_string = '#define %s' % config
                tools.replace_in_file(config_h, '//%s' % config_string, config_string)

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
        else:
            self.copy('*.a', dst='lib', keep_path=False)
        self.copy('*.h', src='include', dst='include')

    def package_info(self):
        self.cpp_info.libs = ['mbedtls', 'mbedx509', 'mbedcrypto']
