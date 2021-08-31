from conans import ConanFile, CMake, tools, python_requires
import os

class LizardConan(ConanFile):
    name = 'lizard'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Apache, MIT'
    no_copy_source = True
    url = 'https://github.com/Devolutions/lizard.git'
    description = 'A 7-Zip packer that sticks'
    settings = 'os', 'arch', 'build_type'
    branch = 'master'
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
        cmake.configure(source_folder=self.name)
        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)
        self.copy('*.h', src='lizard/include/lizard', dst='include/lizard')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
