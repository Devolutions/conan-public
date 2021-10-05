from conans import ConanFile, CMake, tools, python_requires
import os

class Lz4Conan(ConanFile):
    name = 'lz4'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'BSD'
    url = 'https://github.com/lz4/lz4.git'
    description = 'Description'
    settings = 'os', 'arch', 'distro', 'build_type'
    tag = 'v%s' % version
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

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return
        
        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        cmake.configure(source_folder=os.path.join(self.name, 'contrib', 'cmake_unofficial'))

        if self.settings.os == "Windows":
            tools.replace_in_file("CMakeCache.txt", '/MD', '/MT', strict = False)
            cmake.configure(source_folder=os.path.join(self.name, 'contrib', 'cmake_unofficial'))

        cmake.build(args=['--target', 'lz4_static'])

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        elif self.settings.arch == 'universal':
            self.copy('*.a', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib')

        for header in ['lz4.h', 'lz4frame.h', 'lz4hc.h']:
            self.copy(header, src='lz4/lib', dst='include')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
