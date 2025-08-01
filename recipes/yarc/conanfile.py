from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps
from conan.tools.files import copy
from conan.errors import ConanException
import os

class YarcConan(ConanFile):
    name = 'yarc'
    exports_sources = "VERSION"
    generators = "CMakeToolchain"  # Only CMakeToolchain for build tools, CMakeDeps requires host settings
    
    def generate(self):
        # Call cmake_wrapper to set up definitions before generating toolchain
        cmake_dummy = None  # We don't need the CMake object for definitions anymore
        self.cmake_wrapper(cmake_dummy, self.settings, self.options)
        
        # CMakeToolchain and CMakeDeps are automatically generated via generators field
        tc = CMakeToolchain(self)
        # Apply cmake_wrapper definitions if they exist
        if hasattr(self, '_cmake_definitions'):
            self.output.info(f"Applying {len(self._cmake_definitions)} CMake definitions")
            for key, value in self._cmake_definitions.items():
                tc.variables[key] = value
        
        # Only generate CMakeDeps if we have host settings (not just build settings)
        # Build tools (with only os_build, arch_build) don't need CMakeDeps
        try:
            # Check if we have host settings by trying to access build_type
            build_type = self.settings.build_type
            # If we reach here, we have host settings, so generate CMakeDeps if we have dependencies
            if self.dependencies:
                deps = CMakeDeps(self)
                deps.generate()
        except Exception as e:
            # This is a build tool context (only build settings), skip CMakeDeps
            self.output.info("CMakeDeps skipped - build tool context (no host settings)")
    

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
            self.tool_requires('cbake/[*]@devolutions/stable')  # Use tool_requires per gist notes
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
        # For build tools, use Release build type as default
        try:
            cmake.build()
        except Exception as e:
            if "build_type setting should be defined" in str(e):
                # Build tools don't have build_type setting, use CMake directly
                self.run("cmake --build . --config Release")
            else:
                raise

    def package(self):
        base_name = self.name
        
        # Check for executable with and without .exe extension on Windows
        exe_names = [base_name]
        if self.settings.os_build == 'Windows':
            exe_names.append(base_name + '.exe')

        # Look for executable in multiple possible locations
        for exe in exe_names:
            app_path = os.path.join(self.build_folder, 'app', exe)
            app_release_path = os.path.join(self.build_folder, 'app', 'Release', exe)
            root_path = os.path.join(self.build_folder, exe)
            
            if os.path.exists(app_path):
                copy(self, exe, src=os.path.join(self.build_folder, 'app'), dst=os.path.join(self.package_folder, 'bin'))
                return
            elif os.path.exists(app_release_path):
                copy(self, exe, src=os.path.join(self.build_folder, 'app', 'Release'), dst=os.path.join(self.package_folder, 'bin'))
                return
            elif os.path.exists(root_path):
                copy(self, exe, src=self.build_folder, dst=os.path.join(self.package_folder, 'bin'))
                return
        
        # If we get here, no executable was found
        self.output.error(f"Executable {base_name} not found in any expected location")
        raise ConanException(f"Could not find {base_name} executable")
