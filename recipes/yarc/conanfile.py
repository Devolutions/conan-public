from conans import ConanFile, tools, CMake, python_requires
import os

utils = python_requires('utils/latest@devolutions/stable')

class YarcConan(ConanFile):
    name = 'yarc'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    license = 'Devolutions'
    url = 'https://github.com/Devolutions/yarc.git'
    description = 'Yet Another Resource Compiler'
    settings = 'os_build', 'arch_build'
    branch = 'master'

    options = {
        'fPIC': [True, False],
        'cmake_osx_architectures': 'ANY',
        'cmake_osx_deployment_target': 'ANY',
        'ios_deployment_target': 'ANY',
        'shared': [True, False]
    }

    def source(self):
        folder = self.name

        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url, self.branch)

    def build(self):
        cmake = CMake(self, build_type='Release')
        utils.cmake_wrapper(cmake, self.settings, self.options)
        cmake.configure(source_folder=self.name)

        # conan doesn't support properly switching runtimes at the moment,
        # need to use this hack in the meantime
        if self.settings.os_build == 'Windows':
            tools.replace_in_file('CMakeCache.txt', '/MD', '/MT', strict=False)
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
