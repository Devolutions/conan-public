from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps
from conan.tools.files import copy
from conan.errors import ConanException
import os

class YarcConan(ConanFile):
    name = 'yarc'
    exports_sources = "VERSION"
    
    def generate(self):
        # Call cmake_wrapper to set up definitions before generating toolchain
        cmake_dummy = None  # We don't need the CMake object for definitions anymore
        self.cmake_wrapper(cmake_dummy, self.settings, self.options)
        
        tc = CMakeToolchain(self)
        # Apply cmake_wrapper definitions if they exist
        if hasattr(self, '_cmake_definitions'):
            for key, value in self._cmake_definitions.items():
                tc.variables[key] = value
        tc.generate()
        # Only generate CMakeDeps if we have required settings
        try:
            if hasattr(self.settings, 'build_type') and self.dependencies:
                deps = CMakeDeps(self)
                deps.generate()
        except Exception:
            # Skip CMakeDeps generation if build_type is not available
            pass
    

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
        # Only call cmake_layout() if we're in a host context (not build-only context)
        try:
            if self.settings.build_type:
                cmake_layout(self)
        except ConanException:
            # In build-only context, build_type may not be available
            pass

    def build_requirements(self):
        if self.settings.os_build == 'Linux':
            self.tool_requires('cbake/[*]@devolutions/stable')
        else:
            super().build_requirements()

    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = Git(self, folder=folder)
        git.clone(url=self.url, target=".")
        git.checkout(commit=self.branch)

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()

    def package(self):
        exe = self.name
        if self.settings.os_build == 'Windows':
            exe += '.exe'

        if self.settings.os_build == 'Windows':
            copy(self, exe, src=os.path.join(self.build_folder, 'app'), dst=os.path.join(self.package_folder, 'bin'))
        else:
            copy(self, exe, src=os.path.join(self.build_folder, 'app'), dst=os.path.join(self.package_folder, 'bin'))
