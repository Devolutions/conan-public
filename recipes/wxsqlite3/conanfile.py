
from conans import ConanFile, CMake, tools, python_requires
import os

class Sqlite3SecureConan(ConanFile):
    name = 'wxsqlite3'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    url = 'https://github.com/utelle/wxsqlite3'
    description = 'SQLite3 database wrapper for wxWidgets (including SQLite3 encryption extension)'
    homepage = 'https://wiki.wxwidgets.org/Main_Page'
    license = 'LGPL-3.0+ WITH WxWindows-exception-3.1'
    exports_sources = ['CMakeLists.txt']
    generators = 'cmake'
    settings = 'os', 'arch', 'build_type'
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

        self.copy('*.dylib', dst='lib', keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
