from conans import ConanFile, CMake, tools, python_requires
import os

class XppConan(ConanFile):
    name = 'xpp'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Apache, MIT'
    url = 'https://github.com/Devolutions/xpp.git'
    description = 'eXtreme Performance Primitives'
    settings = 'os', 'arch', 'distro', 'build_type'
    branch = 'conan-monorepo'
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
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url, branch=self.branch)

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['XPP_INSTALL'] = 'ON'
        cmake.configure(source_folder=self.name)
        
        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)
        if self.settings.arch == 'universal':
            self.copy('*.h', src='include', dst='include')
        else:
            self.copy('*.h', src='xpp/include/xpp', dst='include/xpp')

    def package_info(self):
        self.cpp_info.libs = ['xpp']
