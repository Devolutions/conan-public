
from conan import ConanFile
from conans import tools  # Keep for compatibility
from conan.tools.cmake import CMake, cmake_layout
import os

class Sqlite3SecureConan(ConanFile):
    name = 'wxsqlite3'
    exports_sources = "VERSION"
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    url = 'https://github.com/utelle/wxsqlite3'
    description = 'SQLite3 database wrapper for wxWidgets (including SQLite3 encryption extension)'
    homepage = 'https://wiki.wxwidgets.org/Main_Page'
    license = 'LGPL-3.0+ WITH WxWindows-exception-3.1'
    exports_sources = ['CMakeLists.txt']
    generators = 'cmake'
    settings = 'os', 'arch', 'build_type'
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

    _source_subfolder = 'source_subfolder'
    _build_subfolder = 'build_subfolder'

    def source(self):
        if self.settings.arch == 'universal':
            return
            
        source_url = 'https://codeload.github.com'
        tools.get("{0}/utelle/wxsqlite3/zip/refs/tags/v{1}".format(source_url, self.version))
        extracted_dir = self.name + '-' + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.arch == 'universal':
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()

    def package(self):
        if self.settings.arch == 'universal':
            return

        if self.settings.os == 'Windows':
            copy(self, '*.lib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
            copy(self, '*.dll', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        else:
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
            copy(self, '*.so', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
            copy(self, '*.dylib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
