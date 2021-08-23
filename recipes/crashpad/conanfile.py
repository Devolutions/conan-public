from conans import ConanFile, CMake, tools, python_requires

import os

class CrashpadConan(ConanFile):
    name = 'crashpad'
    exports = 'VERSION'
    license = 'Apache'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    url = 'https://github.com/Devolutions/crashpad'
    description = 'Crashpad libraries and tools'
    settings = 'os', 'arch', 'build_type'
    tag = '91140a4'
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

    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)
        git.run("submodule update --init")

    def build_requirements(self):
        super().build_requirements()
        self.build_requires('zlib/1.2.11@devolutions/stable')

    def build(self):
        cmake = CMake(self, build_type='Release')
        self.cmake_wrapper(cmake, self.settings, self.options)

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

