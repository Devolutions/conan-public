from conans import ConanFile, tools, CMake, python_requires
import os

class YarcConan(ConanFile):
    name = 'yarc'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Devolutions'
    url = 'https://github.com/Devolutions/yarc.git'
    description = 'Yet Another Resource Compiler'
    settings = 'os_build', 'arch_build'
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

    def build_requirements(self):
        if self.settings.os_build == 'Linux':
            self.build_requires('cbake/latest@devolutions/stable')
        else:
            super().build_requirements()

    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url, self.branch)

    def build(self):
        cmake = CMake(self, build_type='Release')
        self.cmake_wrapper(cmake, self.settings, self.options)
        cmake.configure(source_folder=self.name)
        cmake.build()

    def package(self):
        exe = self.name
        if self.settings.os_build == 'Windows':
            exe += '.exe'

        if self.settings.os_build == 'Windows':
            self.copy(exe, src='app/Release', dst='bin')
        else:
            self.copy(exe, src='app', dst='bin')
