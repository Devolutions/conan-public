from conans import ConanFile, tools, CMake, python_requires
import os

class ZlibConan(ConanFile):
    name = 'zlib'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Zlib'
    url = 'https://github.com/madler/zlib.git'
    description = 'zlib is a general purpose data compression library.'
    settings = 'os', 'arch', 'build_type'
    tag = 'v' + version
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
        if self.settings.arch == 'universal':
            return

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)

        if self.settings.os == 'Windows':
            tools.replace_in_file(os.path.join(folder, 'CMakeLists.txt'),
                "set(CMAKE_DEBUG_POSTFIX \"d\")",
                "set(CMAKE_DEBUG_POSTFIX \"\")", strict=True)

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        cmake.configure(source_folder=self.name)

        if self.settings.os == 'Windows':
            tools.replace_in_file('CMakeCache.txt', '/MD', '/MT', strict=False)
            cmake.configure(source_folder=self.name)

        args = ['--target', 'zlibstatic'] if self.settings.os == 'iOS' else None
        cmake.build(args=args)

    def package(self):
        if self.settings.arch == 'universal':
            self.copy('*.a')
            self.copy('*.h', src='include', dst='include')
            return

        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
            with tools.chdir(os.path.join(self.package_folder, 'lib')):
                os.remove('zlib.lib')
                os.replace('zlibstatic.lib', 'zlib.lib')
        else:
            self.copy('*.a', dst='lib')

        self.copy('zconf.h', dst='include')
        self.copy('zlib.h', src='zlib', dst='include')

    def package_info(self):
        if self.settings.os == 'Windows':
            self.cpp_info.libs = ['zlib']
        else:
            self.cpp_info.libs = ['z']
