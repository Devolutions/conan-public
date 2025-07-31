
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
import os

class PCREConan(ConanFile):
    name = 'pcre2'
    exports_sources = "VERSION"
    

    def set_version(self):
                version_path = os.path.join(os.path.dirname(__file__), "VERSION")
                with open(version_path, 'r') as f:
                    self.version = f.read().strip()
    url = 'https://github.com/bincrafters/conan-pcre2'
    description = 'Perl Compatible Regular Expressions'
    homepage = 'https://www.pcre.org/'
    license = 'BSD-3-Clause'
    exports_sources = ['CMakeLists.txt', 'ios-clear_cache.patch', 'jit_aarch64.patch']
    generators = 'cmake'
    settings = 'os', 'arch', 'distro', 'build_type'
    python_requires = "shared/[1.0.0]@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    options = {
        'fPIC': [True, False],
        'shared': [True, False],
        'build_pcre2_8': [True, False],
        'build_pcre2_16': [True, False],
        'build_pcre2_32': [True, False],
        'support_jit': [True, False]
    }
    default_options = {
        'fPIC': True,
        'shared': False,
        'build_pcre2_8': True,
        'build_pcre2_16': True,
        'build_pcre2_32': True,
        'support_jit': True
    }

    def layout(self):
        cmake_layout(self)

    _source_subfolder = 'source_subfolder'
    _build_subfolder = 'build_subfolder'

    requires = 'zlib/[1.3.1]@devolutions/stable'

    def source(self):
        if self.settings.arch == 'universal':
            return
        
        source_url = 'https://github.com'
        tools.get("{0}/PhilipHazel/pcre2/archive/refs/tags/pcre2-{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + '-' + self.name + '-' + self.version
        os.rename(extracted_dir, self._source_subfolder)

        tools.patch(patch_file='ios-clear_cache.patch', base_path=os.path.join(self._source_subfolder, 'src'))

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        
        cmake.definitions['PCRE2_BUILD_TESTS'] = False
        cmake.definitions['PCRE2_DEBUG'] = self.settings.build_type == 'Debug'
        cmake.definitions['PCRE2_BUILD_PCRE2_8'] = self.options.build_pcre2_8
        cmake.definitions['PCRE2_BUILD_PCRE2_16'] = self.options.build_pcre2_16
        cmake.definitions['PCRE2_BUILD_PCRE2_32'] = self.options.build_pcre2_32
        cmake.definitions['PCRE2_SUPPORT_JIT'] = self.options.support_jit
        cmake.definitions['PCRE2_BUILD_PCRE2GREP'] = 'OFF'

        if self.settings.os == 'Windows':
            cmake.definitions['PCRE2_STATIC_RUNTIME'] = 'ON'

        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()

    def package(self):
        if self.settings.arch == 'universal':
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
            copy(self, '*.h', src=os.path.join(self.source_folder, 'include'), dst=os.path.join(self.package_folder, 'include'))
            return

        if self.settings.os == 'Windows':
            copy(self, '*.lib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        else:
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)

        copy(self, '*pcre2posix.h', src=os.path.join(self.source_folder, self._source_subfolder), dst=os.path.join(self.package_folder, 'include', keep_path=False))
        copy(self, '*pcre2.h', src=os.path.join(self.source_folder, self._build_subfolder), dst=os.path.join(self.package_folder, 'include', keep_path=False))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
