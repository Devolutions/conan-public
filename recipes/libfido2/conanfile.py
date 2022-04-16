from conans import ConanFile, tools, CMake, python_requires
import os

class LibFIDO2Conan(ConanFile):
    name = 'libfido2'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'BSD'
    url = 'https://github.com/awakecoding/libfido2'
    description = 'libfido2'
    settings = 'os', 'arch', 'distro', 'build_type'
    no_copy_source = True
    branch = 'devolutions'
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
        self.build_requires('zlib/1.2.11@devolutions/stable')
        self.build_requires('libcbor/0.9.0@devolutions/stable')
        self.build_requires('libressl/3.4.2@devolutions/stable')

        if self.settings.os == 'Android':
            self.build_requires('libudev-zero/1.0.0@devolutions/stable')

    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.branch)

    def build(self):
        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['BUILD_TOOLS'] = 'OFF'
        cmake.definitions['BUILD_EXAMPLES'] = 'OFF'
        cmake.definitions['BUILD_MANPAGES'] = 'OFF'
        
        if self.options.shared:
            cmake.definitions['BUILD_SHARED_LIBS'] = 'ON'
            cmake.definitions['BUILD_STATIC_LIBS'] = 'OFF'
        else:
            cmake.definitions['BUILD_SHARED_LIBS'] = 'OFF'
            cmake.definitions['BUILD_STATIC_LIBS'] = 'ON'

        zlib_path = self.deps_cpp_info['zlib'].rootpath
        cmake.definitions['ZLIB_ROOT_DIR'] = zlib_path
        cmake.definitions['ZLIB_BIN_DIRS'] = os.path.join(zlib_path, 'bin')
        cmake.definitions['ZLIB_INCLUDE_DIRS'] = os.path.join(zlib_path, 'include')
        cmake.definitions['ZLIB_LIBRARY_DIRS'] = os.path.join(zlib_path, 'lib')

        libcbor_path = self.deps_cpp_info['libcbor'].rootpath
        cmake.definitions['CBOR_ROOT_DIR'] = libcbor_path
        cmake.definitions['CBOR_BIN_DIRS'] = os.path.join(libcbor_path, 'bin')
        cmake.definitions['CBOR_INCLUDE_DIRS'] = os.path.join(libcbor_path, 'include')
        cmake.definitions['CBOR_LIBRARY_DIRS'] = os.path.join(libcbor_path, 'lib')

        libressl_path = self.deps_cpp_info['libressl'].rootpath
        cmake.definitions['CRYPTO_ROOT_DIR'] = libressl_path
        cmake.definitions['CRYPTO_BIN_DIRS'] = os.path.join(libressl_path, 'bin')
        cmake.definitions['CRYPTO_INCLUDE_DIRS'] = os.path.join(libressl_path, 'include')
        cmake.definitions['CRYPTO_LIBRARY_DIRS'] = os.path.join(libressl_path, 'lib')

        if self.settings.os == 'Android':
            libudev_zero_path = self.deps_cpp_info['libudev-zero'].rootpath
            cmake.definitions['UDEV_ROOT_DIR'] = libudev_zero_path

        cmake.configure(source_folder=self.name)
        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.os == 'Windows':
            package_lib_dir = os.path.join(self.package_folder, 'lib')
            os.rename(os.path.join(package_lib_dir, 'fido2_static.lib'), os.path.join(package_lib_dir, 'fido2.lib'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
