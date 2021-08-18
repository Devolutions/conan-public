from conans import ConanFile, tools, CMake, python_requires
import os

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class NngConan(ConanFile):
    name = 'nng'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    license = 'MIT'
    url = 'https://github.com/nanomsg/nng.git'
    description = 'NNG is a socket library that provides several common communication patterns.'
    settings = 'os', 'arch', 'build_type', 'compiler'
    tag = 'v%s' % open(os.path.join('.', 'VERSION'), 'r').read().rstrip()

    options = {
        'fPIC': [True, False],
        'cmake_osx_architectures': 'ANY',
        'cmake_osx_deployment_target': 'ANY',
        'ios_deployment_target': 'ANY',
        'shared': [True, False]
    }

    def build_requirements(self):
        self.build_requires('mbedtls/2.16.0-6@devolutions/stable')

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

            cmake.definitions['NNG_TESTS'] = 'OFF'
            cmake.definitions['NNG_TOOLS'] = 'OFF'
            cmake.definitions['NNG_ENABLE_DOC'] = 'OFF'
            cmake.definitions['NNG_ENABLE_TLS'] = 'ON'
            cmake.definitions['NNG_ENABLE_HTTP'] = 'ON'
            cmake.definitions['NNG_TRANSPORT_TLS'] = 'ON'
            cmake.definitions['NNG_TRANSPORT_WSS'] = 'ON'
            cmake.definitions['NNG_ENABLE_NNGCAT'] = 'ON'
            cmake.definitions['NNG_ENABLE_COVERAGE'] = 'OFF'
            cmake.definitions['NNG_ENABLE_NNGCAT'] = 'OFF'

            if self.settings.os == 'Macos':
                cmake.definitions['CMAKE_C_FLAGS'] = '-DNNG_USE_GETTIMEOFDAY'

            cmake.definitions['MBEDTLS_TLS_LIBRARY'] = os.path.join(self.deps_cpp_info['mbedtls'].rootpath, 'lib', 'libmbedtls.a')
            cmake.definitions['MBEDTLS_CRYPTO_LIBRARY'] = os.path.join(self.deps_cpp_info['mbedtls'].rootpath, 'lib', 'libmbedcrypto.a')
            cmake.definitions['MBEDTLS_X509_LIBRARY'] = os.path.join(self.deps_cpp_info['mbedtls'].rootpath, 'lib', 'libmbedx509.a')
            cmake.definitions['MBEDTLS_INCLUDE_DIR'] = os.path.join(self.deps_cpp_info['mbedtls'].rootpath, 'include')

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
        self.copy('*.h', src='nng/include', dst='include')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == 'Linux' or self.settings.os == 'Macos':
            for flag in ['-lpthread', '-lm', '-ldl']:
                self.cpp_info.sharedlinkflags.append(flag)
