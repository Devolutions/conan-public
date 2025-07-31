from conan import ConanFile
from conans import tools  # Keep for compatibility
from conan.tools.files import replace_in_file, copy, load, save
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os

class MbedtlsConan(ConanFile):
    name = 'mbedtls'
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    license = 'Apache 2.0'
    url = 'https://github.com/Mbed-TLS/mbedtls'
    description = 'An open source, portable, easy to use, readable and flexible SSL library'
    settings = 'os', 'arch', 'distro', 'build_type'
    python_requires = "shared/[1.0.0]@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    exports = ['VERSION',
        'patches/0001-add-windows-mutex-implementation-for-threading.patch',
        'patches/0002-aes-ni-use-target-attributes-for-32-bit-intrinsics.patch',
        'patches/0003-fix-build-for-windows-arm64-neon-and-aes-extensions.patch',
        'patches/0004-add-support-for-mbedtls-ssl-verify-external-authmode.patch',
        'patches/0005-fix-tls13-keys-cast-build-warning.patch']

    options = {
        'fPIC': [True, False],
        'shared': [True, False]
    }
    default_options = {
        'fPIC': True,
        'shared': False
    }

    def layout(self):
        cmake_layout(self)

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name
        tag = 'v%s' % (self.version)
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, tag))
        git = Git(self, folder=folder)
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
        mbedtls_configs.extend(['MBEDTLS_SSL_PROTO_TLS1_3'])

        if self.settings.os == 'Windows':
            cmake.definitions['MSVC_STATIC_RUNTIME'] = 'ON'

        if self.settings.os == 'Windows':
            mbedtls_configs.extend(['MBEDTLS_THREADING_WINDOWS'])
        else:
            mbedtls_configs.extend(['MBEDTLS_THREADING_PTHREAD'])

        config_h = os.path.join(self.source_folder, 'mbedtls', 'include', 'mbedtls', 'mbedtls_config.h')

        for config in mbedtls_configs:
            config_string = '#define %s' % config
            replace_in_file(self, config_h, '//%s' % config_string, config_string)

        cmake.configure()

        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.os == 'Windows':
            copy(self, '*.lib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        else:
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        copy(self, '*.h', src=os.path.join(self.source_folder, 'include'), dst=os.path.join(self.package_folder, 'include'))

    def package_info(self):
        self.cpp_info.libs = ['mbedtls', 'mbedx509', 'mbedcrypto', 'everest', 'p256m']

        if self.settings.os == 'Windows':
            for lib in ['bcrypt']:
                self.cpp_info.libs.append(lib)
