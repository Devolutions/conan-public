from conans import ConanFile, CMake, tools, python_requires
import os

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class Lz4Conan(ConanFile):
    name = 'lz4'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    license = 'BSD, GPLv2'
    url = 'https://github.com/lz4/lz4.git'
    description = 'Description'
    settings = 'os', 'arch', 'build_type', 'compiler'
    tag = 'v%s' % upstream_version

    options = {
        'fPIC': [True, False],
        'cmake_osx_architectures': 'ANY',
        'cmake_osx_deployment_target': 'ANY',
        'ios_deployment_target': 'ANY',
        'shared': [True, False]
    }

    def source(self):
        if self.settings.arch != 'universal':
            folder = self.name

            self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
            git = tools.Git(folder=folder)
            git.clone(self.url)
            git.checkout(self.tag)

    def build(self):
        if self.settings.arch == 'universal':
            lipo.create(self, self.build_folder)
        else:
            cmake = CMake(self)
            utils.cmake_wrapper(cmake, self.settings, self.options)
            cmake.configure(source_folder=os.path.join(self.name, 'contrib', 'cmake_unofficial'))

            # conan doesn't support properly switching runtimes at the moment,
            # need to use this hack in the meantime
            if self.settings.os == 'Windows':
                tools.replace_in_file('CMakeCache.txt', '/MD', '/MT', strict=False)
                cmake.configure(source_folder=os.path.join(self.name, 'contrib', 'cmake_unofficial'))

            cmake.build(args=['--target', 'lz4_static'])

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        elif self.settings.os == 'iOS' and self.settings.arch == 'universal':
            self.copy('*.a', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib')

        for header in ['lz4.h', 'lz4frame.h', 'lz4hc.h']:
            self.copy(header, src='lz4/lib', dst='include')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
