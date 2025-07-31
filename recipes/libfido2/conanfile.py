from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os, shutil

class LibFIDO2Conan(ConanFile):
    name = 'libfido2'
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    license = 'BSD'
    url = 'https://github.com/PowerShell/libfido2'
    description = 'libfido2'
    settings = 'os', 'arch', 'distro', 'build_type'
    no_copy_source = True
    python_requires = "shared/[1.0.0]@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    exports = ['VERSION',
        'patches/1.10.0/0001-fix-cmake-dependency-management.patch',
        'patches/1.10.0/0002-fix-crypto-explicit_bzero-conflict.patch',
        'patches/1.10.0/0003-use-linux-hid-backend-for-android.patch',
        'patches/1.14.0/0001-fix-cmake-dependency-management.patch',
        'patches/1.14.0/0002-fix-crypto-explicit_bzero-conflict.patch',
        'patches/1.14.0/0003-use-linux-hid-backend-for-android.patch']

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

    def build_requirements(self):
        super().build_requirements()
        self.tool_requires('zlib/[1.3.1]@devolutions/stable')
        self.tool_requires('libcbor/[0.10.2]@devolutions/stable')
        self.tool_requires('libressl/[3.8.2]@devolutions/stable')

        if self.settings.os == 'Android':
            self.tool_requires('libudev-zero/[1.0.0]@devolutions/stable')

    def source(self):
        folder = self.name
        tag = self.version
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, tag))
        git = Git(self, folder=folder)
        git.clone(self.url)
        git.checkout(tag)

        patches_dir = os.path.join(self.recipe_folder, "patches", self.version)
        if os.path.isdir(patches_dir):
            for patch_file in [f for f in os.listdir(patches_dir) if f.endswith('.patch')]:
                patch_path = os.path.join(patches_dir, patch_file)
                self.output.info('Applying patch: %s' % patch_path)
                tools.patch(base_path=folder, patch_file=patch_path)

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

        zlib_path = self.dependencies['zlib'].package_folder
        cmake.definitions['ZLIB_ROOT_DIR'] = zlib_path
        cmake.definitions['ZLIB_BIN_DIRS'] = os.path.join(zlib_path, 'bin')
        cmake.definitions['ZLIB_INCLUDE_DIRS'] = os.path.join(zlib_path, 'include')
        cmake.definitions['ZLIB_LIBRARY_DIRS'] = os.path.join(zlib_path, 'lib')

        libcbor_path = self.dependencies['libcbor'].package_folder
        cmake.definitions['CBOR_ROOT_DIR'] = libcbor_path
        cmake.definitions['CBOR_BIN_DIRS'] = os.path.join(libcbor_path, 'bin')
        cmake.definitions['CBOR_INCLUDE_DIRS'] = os.path.join(libcbor_path, 'include')
        cmake.definitions['CBOR_LIBRARY_DIRS'] = os.path.join(libcbor_path, 'lib')

        libressl_path = self.dependencies['libressl'].package_folder
        cmake.definitions['CRYPTO_ROOT_DIR'] = libressl_path
        cmake.definitions['CRYPTO_BIN_DIRS'] = os.path.join(libressl_path, 'bin')
        cmake.definitions['CRYPTO_INCLUDE_DIRS'] = os.path.join(libressl_path, 'include')
        cmake.definitions['CRYPTO_LIBRARY_DIRS'] = os.path.join(libressl_path, 'lib')

        if self.settings.os == 'Android':
            libudev_zero_path = self.dependencies['libudev-zero'].package_folder
            cmake.definitions['UDEV_ROOT_DIR'] = libudev_zero_path

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.os == 'Windows':
            package_lib_dir = os.path.join(self.package_folder, 'lib')
            os.rename(os.path.join(package_lib_dir, 'fido2_static.lib'), os.path.join(package_lib_dir, 'fido2.lib'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
