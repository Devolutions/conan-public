from conans import ConanFile, tools, CMake, python_requires
import os

class LibreSSLConan(ConanFile):
    name = 'libressl'
    license = 'BSD'
    url = 'https://www.libressl.org/'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    description = 'LibreSSL'
    settings = 'os', 'arch', 'distro', 'build_type'
    no_copy_source = False
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    exports = ['VERSION',
        'patches/3.4.2/0001-normalize-library-output-names.patch',
        'patches/3.4.2/0002-set-default-output-directories.patch',
        'patches/3.8.2/0001-normalize-library-output-names.patch',
        'patches/3.8.2/0002-set-default-output-directories.patch']

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

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name
        source_url = 'https://github.com/libressl/portable/releases/download/v%s/libressl-%s.tar.gz' % (self.version, self.version)
        self.output.info('Downloading release: %s' % source_url)
        tools.get(
            source_url,
            sha256='290cdf1b53c086255dc302f118b98602a444e9ae6d11e9bfdd8c9b1b60aa3a22',
            destination=folder,
            strip_root=True,
        )

        patches_dir = os.path.join(self.recipe_folder, "patches", self.version)
        if os.path.isdir(patches_dir):
            for patch_file in os.listdir(patches_dir):
                patch_path = os.path.join(patches_dir, patch_file)
                self.output.info('Applying patch: %s' % patch_path)
                tools.patch(base_path=folder, patch_file=patch_path)

        if self.settings.os == 'iOS':
            tools.replace_in_file(os.path.join(folder, 'CMakeLists.txt'),
                "check_function_exists(syslog HAVE_SYSLOG)",
                "#check_function_exists(syslog HAVE_SYSLOG)")

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        cmake.definitions['USE_STATIC_MSVC_RUNTIMES'] = 'ON'
        cmake.definitions['CMAKE_INSTALL_LIBEXECDIR'] = "lib"
        cmake.definitions['CMAKE_SHARED_LIBRARY_PREFIX'] = "lib"
        cmake.definitions['CMAKE_STATIC_LIBRARY_PREFIX'] = "lib"
        cmake.definitions['BUILD_SHARED_LIBS'] = 'ON' if self.options.shared else 'OFF'

        if self.settings.os == 'Windows' and self.settings.arch == 'armv8':
            cmake.definitions['CMAKE_SYSTEM_PROCESSOR'] = 'aarch64'

        if self.settings.os == 'iOS' or self.settings.os == 'Android':
            cmake.definitions['LIBRESSL_APPS'] = 'OFF'
        else:
            cmake.definitions['LIBRESSL_APPS'] = 'ON'
            
        cmake.definitions['LIBRESSL_TESTS'] = 'OFF'

        cmake.configure(source_folder=self.name)
        
        cmake.build()
        cmake.install()

    def package(self):
        return

    def package_info(self):
        if self.settings.os == 'Windows':
            self.cpp_info.libs = ['libssl', 'libcrypto', 'libtls']
        else:
            self.cpp_info.libs = ['ssl', 'crypto', 'tls']

        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.OPENSSL_DIR = self.package_folder
