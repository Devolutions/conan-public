from conans import ConanFile, CMake, tools, python_requires

import os

utils = python_requires('utils/latest@devolutions/stable')

class CrashpadConan(ConanFile):
    name = 'crashpad'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    license = 'Apache'
    version = '%s-%s' % (upstream_version, revision)
    url = 'https://github.com/Devolutions/crashpad'
    description = 'Crashpad libraries and tools'
    settings = 'os', 'arch', 'build_type', 'compiler'
    tag = '91140a4'

    options = {
        'fPIC': [True, False],
        'cmake_osx_architectures': 'ANY',
        'cmake_osx_deployment_target': 'ANY',
        'ios_deployment_target': 'ANY',
        'shared': [True, False]
    }

    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)
        git.run("submodule update --init")

    def build_requirements(self):
        self.build_requires('zlib/1.2.11-5@devolutions/stable')

    def build(self):
        cmake = CMake(self, build_type='Release')
        utils.cmake_wrapper(cmake, self.settings, self.options)

        if self.settings.os == 'Windows':
            cmake.definitions['MSVC_RUNTIME'] = 'static'

        cmake.definitions['ZLIB_LIBRARY'] = os.path.join(self.deps_cpp_info['zlib'].rootpath, 'lib', 'zlib.lib')
        cmake.definitions['ZLIB_INCLUDE_DIR'] = os.path.join(self.deps_cpp_info['zlib'].rootpath, 'include')

        cmake.configure(source_folder=self.name)
        cmake.build()

    def package(self):
        self.copy('*crashpad_handler.exe', dst='bin', keep_path=False, symlinks=True)
        self.copy('*generate_dump.exe', dst='bin', keep_path=False, symlinks=True)
        self.copy('*crashpad_*.lib', dst='lib', keep_path=False, symlinks=True)
        self.copy('*mini_chromium.lib', dst='lib', keep_path=False, symlinks=True)
        self.copy('*.h', src='crashpad/vendor/mini_chromium', dst='include/mini_chromium', keep_path=True, symlinks=True)
        self.copy('*.h', src='crashpad/vendor/crashpad', dst='include', keep_path=True, symlinks=True)
        self.copy('*.h', src='crashpad/vendor/include', dst='include', keep_path=True, symlinks=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        included_dirs = ["include/mini_chromium", "include"]

        if self.settings.os == 'Windows':
            included_dirs.append("include/compat/win")

        self.cpp_info.includedirs = included_dirs

