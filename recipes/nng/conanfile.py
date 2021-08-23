from conans import ConanFile, tools, CMake, python_requires
import os

class NngConan(ConanFile):
    name = 'nng'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    url = 'https://github.com/nanomsg/nng.git'
    license = 'MIT'
    description = 'NNG is a socket library that provides several common communication patterns.'
    settings = 'os', 'arch', 'build_type'
    tag = 'v%s' % version
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

    def build_requirements(self):
        super().build_requirements()
        self.build_requires('mbedtls/2.16.0@devolutions/stable')

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

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
