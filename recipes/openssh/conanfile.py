from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os, shutil

class OpenSSHConan(ConanFile):
    name = 'openssh'
    exports_sources = "VERSION"
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    license = 'BSD'
    url = 'https://github.com/openssh/openssh-portable'
    description = 'OpenSSH'
    settings = 'os', 'arch', 'distro', 'build_type'
    no_copy_source = False
    python_requires = "shared/[1.0.0]@devolutions/stable"
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

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        super().build_requirements()
        self.tool_requires('zlib/[1.3.1]@devolutions/stable')
        self.tool_requires('libcbor/[0.10.2]@devolutions/stable')
        self.tool_requires('libressl/[3.8.2]@devolutions/stable')
        self.tool_requires('libfido2/[1.14.0]@devolutions/stable')

    def source(self):
        folder = self.name
        version_parts = self.version.split('.')
        self.branch = f"V_{version_parts[0]}_{version_parts[1]}_P1"
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = Git(self, folder=folder)
        git.clone(url=self.url, target=".")
        git.checkout(self.branch)

        git_distro = Git(self, folder="openssh-distro")
        git_distro.clone("https://github.com/Devolutions/openssh-distro")
        git_distro.checkout('master')
        version_dir = 'v%s' % (self.version)
        patches_dir = os.path.join(os.getcwd(), "openssh-distro", "patches", version_dir)
        if os.path.isdir(patches_dir):
            patch_files = sorted([f for f in os.listdir(patches_dir) if f.endswith('.patch')])
            for patch_file in patch_files:
                # quick and dirty dos2unix-like to work around .gitattributes for *.patch being ignored
                patch_path = os.path.join(patches_dir, patch_file)
                with open(patch_path, 'r', encoding='utf-8', newline='') as file:
                    content = file.read().replace('\r\n', '\n')
                with open(patch_path, 'w', encoding='utf-8', newline='\n') as file:
                    file.write(content)
                git_cmd = 'apply --whitespace=nowarn %s' % (patch_path)
                git.run(git_cmd)

    def build(self):
        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['USE_PREBUILT_DEPS'] = 'OFF'

        zlib_path = self.dependencies['zlib'].package_folder
        cmake.definitions['ZLIB_INCLUDE_DIR'] = os.path.join(zlib_path, 'include')
        cmake.definitions['ZLIB_LIBRARY_DIR'] = os.path.join(zlib_path, 'lib')

        libressl_path = self.dependencies['libressl'].package_folder
        cmake.definitions['LIBRESSL_INCLUDE_DIR'] = os.path.join(libressl_path, 'include')
        cmake.definitions['LIBRESSL_LIBRARY_DIR'] = os.path.join(libressl_path, 'lib')

        libfido2_path = self.dependencies['libfido2'].package_folder
        cmake.definitions['FIDO2_INCLUDE_DIR'] = os.path.join(libfido2_path, 'include')
        cmake.definitions['FIDO2_LIBRARY_DIR'] = os.path.join(libfido2_path, 'lib')

        libcbor_path = self.dependencies['libcbor'].package_folder
        cmake.definitions['CBOR_INCLUDE_DIR'] = os.path.join(libcbor_path, 'include')
        cmake.definitions['CBOR_LIBRARY_DIR'] = os.path.join(libcbor_path, 'lib')

        cmake.configure()
        cmake.build()
        cmake.install()
