from conans import ConanFile, CMake, tools, python_requires
import os
from shutil import copy, copyfile, rmtree, copytree

class WinprConan(ConanFile):
    name = 'winpr'
    exports = 'VERSION'
    # exports_sources = ['FindWinPR.cmake']
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Apache 2.0'
    url = 'https://github.com/Devolutions/FreeRDP.git'
    description = 'FreeRDP is a free remote desktop protocol client'
    settings = 'os', 'arch', 'distro', 'build_type'
    branch = 'devolutions-rdp-rebase-2'
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
        self.build_requires('zlib/1.2.11@devolutions/stable')

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = 'freerdp'
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.branch)

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        # folder = os.path.join(self.source_folder, 'freerdp')
        # rmtree(folder, ignore_errors=True)
        # copytree("/opt/wayk/dev/FreeRDP", folder)

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['WITH_WINPR_TOOLS'] = 'OFF'
        cmake.definitions['WITH_MBEDTLS'] = 'ON'
        cmake.definitions['WITH_OPENSSL'] = 'OFF'

        if self.settings.os == 'Linux':
            cmake.definitions['WITH_LIBSYSTEMD'] = 'OFF'

        if self.settings.os == 'Windows':
            cmake.definitions['MSVC_RUNTIME'] = 'static'

        mbedtls_path = self.deps_cpp_info['mbedtls'].rootpath
        zlib_path = self.deps_cpp_info['zlib'].rootpath
        cmake.definitions['CMAKE_PREFIX_PATH'] = '%s;%s' % (mbedtls_path, zlib_path)
        
        # Android
        cmake.definitions['CMAKE_FIND_ROOT_PATH'] = '%s;%s' % (mbedtls_path, zlib_path)

        cmake.configure(source_folder=os.path.join("freerdp", self.name))

        cmake.build()

    def package(self):
        # self.copy("FindWinPR.cmake", ".", ".")

        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            # tools.rename("libwinpr/libwinpr3.a", "libwinpr/libwinpr.a")
            self.copy('*.a', dst='lib', keep_path=False)

        if self.settings.arch == 'universal':
            self.copy('*.h')
        else:
            self.copy('config.h', dst='include/winpr')
            self.copy('*.h', src='include/winpr', dst='include/winpr')
            self.copy('*.h', src='freerdp/winpr/include/winpr', dst='include/winpr')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == 'Windows':
            for lib in ['ws2_32', 'dbghelp', 'crypt32', 'shell32', 'shlwapi']:
                self.cpp_info.libs.append(lib)
        elif self.settings.os == 'Linux' or self.settings.os == 'Macos':
            for lib in ['pthread', 'm', 'dl']:
                self.cpp_info.libs.append(lib)
