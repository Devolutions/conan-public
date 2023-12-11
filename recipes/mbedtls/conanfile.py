from conans import ConanFile, CMake, tools, python_requires
import os

class MbedtlsConan(ConanFile):
    name = 'mbedtls'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Apache 2.0'
    url = 'https://github.com/Mbed-TLS/mbedtls'
    description = 'An open source, portable, easy to use, readable and flexible SSL library'
    settings = 'os', 'arch', 'distro', 'build_type'
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    exports = ['VERSION',
        'patches/0001-add-windows-mutex-implementation-for-threading.patch',
        'patches/0002-aes-ni-use-target-attributes-for-32-bit-intrinsics.patch',
        'patches/0003-fix-build-for-windows-arm64-neon-and-aes-extensions.patch',
        'patches/0004-add-support-for-mbedtls-ssl-verify-external-authmode.patch']

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
        tag = 'v%s' % (self.version)
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(tag)

        patches_dir = os.path.join(self.recipe_folder, "patches")
        if os.path.isdir(patches_dir):
            for patch_file in os.listdir(patches_dir):
                patch_path = os.path.join(patches_dir, patch_file)
                self.output.info('Applying patch: %s' % patch_path)
                tools.patch(base_path=folder, patch_file=patch_path)

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['ENABLE_TESTING'] = 'OFF'
        cmake.definitions['ENABLE_PROGRAMS'] = 'OFF'

        mbedtls_configs = ['MBEDTLS_THREADING_C']

        if self.settings.os == 'Windows':
            cmake.definitions['MSVC_STATIC_RUNTIME'] = 'ON'

        if self.settings.os == 'Windows':
            mbedtls_configs.extend(['MBEDTLS_THREADING_WINDOWS'])
        else:
            mbedtls_configs.extend(['MBEDTLS_THREADING_PTHREAD'])

        config_h = os.path.join(self.source_folder, 'mbedtls', 'include', 'mbedtls', 'mbedtls_config.h')

        for config in mbedtls_configs:
            config_string = '#define %s' % config
            tools.replace_in_file(config_h, '//%s' % config_string, config_string)

        cmake.configure(source_folder=self.name)

        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)
        self.copy('*.h', src='include', dst='include')

    def package_info(self):
        self.cpp_info.libs = ['mbedtls', 'mbedx509', 'mbedcrypto', 'everest', 'p256m']

        if self.settings.os == 'Windows':
            for lib in ['bcrypt']:
                self.cpp_info.libs.append(lib)
