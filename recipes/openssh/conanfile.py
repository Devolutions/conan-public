from conans import ConanFile, tools, CMake, python_requires
import os, shutil

class OpenSSHConan(ConanFile):
    name = 'openssh'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'BSD'
    url = 'https://github.com/awakecoding/openssh-portable'
    description = 'OpenSSH'
    settings = 'os', 'arch', 'distro', 'build_type'
    no_copy_source = False
    branch = 'devolutions'
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    use_prebuilt_msdeps = False

    options = {
        'fPIC': [True, False],
        'shared': [True, False]
    }
    default_options = {
        'fPIC': True,
        'shared': True
    }

    def build_requirements(self):
        super().build_requirements()
        self.build_requires('zlib/1.2.11@devolutions/stable')
        self.build_requires('libcbor/0.9.0@devolutions/stable')
        self.build_requires('libressl/3.4.2@devolutions/stable')
        self.build_requires('libfido2/1.10.0@devolutions/stable')

    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.branch)

    def build(self):
        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['USE_PREBUILT_DEPS'] = 'OFF'

        zlib_path = self.deps_cpp_info['zlib'].rootpath
        cmake.definitions['ZLIB_INCLUDE_DIR'] = os.path.join(zlib_path, 'include')
        cmake.definitions['ZLIB_LIBRARY_DIR'] = os.path.join(zlib_path, 'lib')

        libressl_path = self.deps_cpp_info['libressl'].rootpath
        cmake.definitions['LIBRESSL_INCLUDE_DIR'] = os.path.join(libressl_path, 'include')
        cmake.definitions['LIBRESSL_LIBRARY_DIR'] = os.path.join(libressl_path, 'lib')

        libfido2_path = self.deps_cpp_info['libfido2'].rootpath
        cmake.definitions['FIDO2_INCLUDE_DIR'] = os.path.join(libfido2_path, 'include')
        cmake.definitions['FIDO2_LIBRARY_DIR'] = os.path.join(libfido2_path, 'lib')

        libcbor_path = self.deps_cpp_info['libcbor'].rootpath
        cmake.definitions['CBOR_INCLUDE_DIR'] = os.path.join(libcbor_path, 'include')
        cmake.definitions['CBOR_LIBRARY_DIR'] = os.path.join(libcbor_path, 'lib')

        cmake.configure(source_folder=self.name)
        cmake.build()
        cmake.install()
