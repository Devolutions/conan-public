from conans import ConanFile, CMake, tools, python_requires
import os

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class FreevncConan(ConanFile):
    name = 'freevnc'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'proprietary'
    url = 'git@github.com:Devolutions/freevnc.git'
    description = 'VNC/ARD implementation'
    settings = 'os', 'arch', 'build_type'
    tag = "conan-monorepo"

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
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)

    def build(self):
        if self.settings.arch == 'universal':
            lipo.create(self, self.build_folder)
            return

        cmake = CMake(self)
        utils.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['WITH_APPS'] = 'OFF'

        if self.settings.os == 'Windows':
            cmake.definitions['MSVC_RUNTIME'] = 'static'

        if self.settings.arch in ['x86', 'x86_64']:
            cmake.definitions['WITH_SSE2'] = 'ON'
        else:
            if self.settings.os != 'Windows':
                cmake.definitions['WITH_NEON'] = 'ON'

        cmake.configure(source_folder=self.name)
        cmake.build()

    def package(self):
        if self.settings.arch == 'universal':
            self.copy('*.a', dst='lib', keep_path=False)
            self.copy('*.h', src='include', dst='include')
            return

        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)

        if self.settings.os == 'Windows':
            self.copy('*.dll', dst='lib', keep_path=False)
        elif self.settings.os == 'Macos':
            self.copy('*.dylib', dst='lib', keep_path=False)
        elif self.settings.os == 'iOS':
            self.copy('*.a', dst='lib', keep_path=False)
        else:
            self.copy('*.so', dst='lib', keep_path=False)

        self.copy('*.h', src='freevnc/include/freevnc', dst='include/freevnc') # CMAKE_SOURCE_DIR
        self.copy('*.h', src='include/freevnc', dst='include/freevnc') # CMAKE_BINARY_DIR

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == 'Windows':
            for lib in ['ws2_32', 'dbghelp', 'crypt32']:
                self.cpp_info.libs.append(lib)
        elif self.settings.os == 'Linux' or self.settings.os == 'Macos':
            for lib in ['-lpthread', '-lm', '-ldl']:
                self.cpp_info.libs.append(lib)
