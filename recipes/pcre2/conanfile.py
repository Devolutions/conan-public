
from conans import ConanFile, CMake, tools, python_requires
import os

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class PCREConan(ConanFile):
    name = 'pcre2'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    url = 'https://github.com/bincrafters/conan-pcre2'
    description = 'Perl Compatible Regular Expressions'
    homepage = 'https://www.pcre.org/'
    license = 'BSD-3-Clause'
    exports_sources = ['CMakeLists.txt', 'ios-clear_cache.patch', 'jit_aarch64.patch']
    generators = 'cmake'
    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {
        'build_pcre2_8': [True, False],
        'build_pcre2_16': [True, False],
        'build_pcre2_32': [True, False],
        'support_jit': [True, False],
        'fPIC': [True, False],
        'cmake_osx_architectures': 'ANY',
        'cmake_osx_deployment_target': 'ANY',
        'ios_deployment_target': 'ANY',
        'shared': [True, False]
    }

    default_options = { 'shared': False, 'build_pcre2_8': True, 'build_pcre2_16': True, 'build_pcre2_32': True, 'support_jit': True }

    _source_subfolder = 'source_subfolder'
    _build_subfolder = 'build_subfolder'

    requires = 'zlib/1.2.11-5@devolutions/stable'

    def source(self):
        if self.settings.arch == 'universal':
            return
        
        source_url = 'https://ftp.pcre.org'
        tools.get("{0}/pub/pcre/pcre2-{1}.tar.gz".format(source_url, self.upstream_version))
        extracted_dir = self.name + '-' + self.upstream_version
        os.rename(extracted_dir, self._source_subfolder)

        tools.patch(patch_file='ios-clear_cache.patch', base_path=os.path.join(self._source_subfolder, 'src'))

    def build(self):
        if self.settings.arch == 'universal':
            lipo.create(self, self.build_folder)
            return

        cmake = CMake(self)
        utils.cmake_wrapper(cmake, self.settings, self.options)
        
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
            self.copy('*.a', dst='lib', keep_path=False)
            self.copy('*.h', src='include', dst='include')
            return

        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)

        self.copy('*pcre2posix.h', src=self._source_subfolder, dst='include', keep_path=False)
        self.copy('*pcre2.h', src=self._build_subfolder, dst='include', keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
