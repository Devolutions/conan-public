from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy
import os

class WebViewConan(ConanFile):
    name = 'webview'
    exports_sources = "VERSION"
    
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    description = 'GTK WebKitWebKitView wrapper'
    settings = 'os', 'arch', 'distro', 'build_type'
    generators = 'cmake'
    python_requires = "shared/[1.0.0]@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    exports_sources = ['CMakeLists.txt', 'conanfile.txt', 'cmake/*', 'src/*']

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
        super().build_requirements()
        self.tool_requires('cbake/[*]@devolutions/stable')

    def build(self):
        if self.settings.arch == 'universal':
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        
        cmake.configure(build_folder="build")
        cmake.build()

    def package(self):
        if self.settings.arch == 'universal':
            return

        copy(self, '*.so', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
