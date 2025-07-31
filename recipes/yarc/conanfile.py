from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os

class YarcConan(ConanFile):
    name = 'yarc'
    exports_sources = "VERSION"
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    license = 'Devolutions'
    url = 'https://github.com/Devolutions/yarc.git'
    description = 'Yet Another Resource Compiler'
    settings = 'os_build', 'arch_build'
    branch = 'master'
    python_requires = "shared/[1.0.0]@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    options = {
        'fPIC': [True, False],
        'shared': [True, False]
    }
    default_options = {
        'fPIC': True,
        'shared': False
    }

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        if self.settings.os_build == 'Linux':
            self.tool_requires('cbake/[*]@devolutions/stable')
        else:
            super().build_requirements()

    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = Git(self, folder=folder)
        git.clone(self.url, self.branch)

    def build(self):
        cmake = CMake(self, build_type='Release')
        self.cmake_wrapper(cmake, self.settings, self.options)
        cmake.configure()
        cmake.build()

    def package(self):
        exe = self.name
        if self.settings.os_build == 'Windows':
            exe += '.exe'

        if self.settings.os_build == 'Windows':
            copy(self, exe, src=os.path.join(self.source_folder, 'app/Release'), dst=os.path.join(self.package_folder, 'bin'))
        else:
            copy(self, exe, src=os.path.join(self.source_folder, 'app'), dst=os.path.join(self.package_folder, 'bin'))
