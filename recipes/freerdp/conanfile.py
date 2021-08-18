from conans import ConanFile, CMake, tools, python_requires
import os
from shutil import copyfile

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class FreerdpConan(ConanFile):
    name = 'freerdp'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    license = 'Apache 2.0'
    no_copy_source = True
    url = 'https://github.com/Devolutions/FreeRDP.git'
    description = 'FreeRDP is a free remote desktop protocol client'
    settings = 'os', 'arch', 'build_type', 'compiler'
    branch = 'devolutions-rdp2'

    options = {
        'fPIC': [True, False],
        'cmake_osx_architectures': 'ANY',
        'cmake_osx_deployment_target': 'ANY',
        'ios_deployment_target': 'ANY',
        'shared': [True, False]
    }

    def build_requirements(self):
        self.build_requires('openssl/1.1.1d-4@devolutions/stable')
        self.build_requires('winpr/2.3.2-7@devolutions/stable')
        self.build_requires('mbedtls/2.16.0-6@devolutions/stable')
        self.build_requires('zlib/1.2.11-5@devolutions/stable')

    def source(self):
        if self.settings.arch != 'universal':
            folder = self.name

            self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
            git = tools.Git(folder=folder)
            git.clone(self.url)
            git.checkout(self.branch)

            devolutions_rdp_dir = os.path.join(folder, 'DevolutionsRdp')
            for r, d, f in os.walk(os.path.join(devolutions_rdp_dir, "patches")):
                for item in sorted(f):
                    if '.patch' in item:
                        print("applying patch: " + item)
                        tools.patch(base_path=folder, patch_file=os.path.join(r, item))

            with open(os.path.join(folder, "CMakeLists.txt"), 'a') as file:
                file.write('\nadd_subdirectory(DevolutionsRdp)')
            
    def build(self):
        if self.settings.arch == 'universal':
            lipo.create(self, self.build_folder)
            return

        cmake = CMake(self)
        utils.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['WINPR_IMPORT'] = 'ON'
        cmake.definitions['ENABLE_TESTING'] = 'OFF'
        cmake.definitions['WITH_CLIENT_COMMON'] = 'ON'
        cmake.definitions['WITH_CLIENT'] = 'OFF'
        cmake.definitions['WITH_SERVER'] = 'OFF'
        cmake.definitions['WITH_WAYLAND'] = 'OFF'
        cmake.definitions['WITH_MANPAGES'] = 'OFF'
        cmake.definitions['WITH_FFMPEG'] = 'OFF'
        cmake.definitions['WITH_VAAPI'] = 'OFF'
        cmake.definitions['WITH_GSTREAMER_1_0'] = 'OFF'
        cmake.definitions['WITH_GSTREAMER_0_10'] = 'OFF'
        cmake.definitions['WITH_LIBSYSTEMD'] = 'OFF'
        cmake.definitions['WITH_OPENSSL'] = 'ON'
        cmake.definitions['WITH_ALSA'] = 'OFF'
        cmake.definitions['CHANNEL_URBDRC'] = 'OFF'

        if self.settings.os == 'Linux' or self.settings.os == 'Macos':
            cmake.definitions['WITH_CUPS'] = 'ON'

        if self.settings.arch in ['x86', 'x86_64']:
            cmake.definitions['WITH_SSE2'] = 'ON'
        else:
            cmake.definitions['WITH_SSE2'] = 'OFF'
            if self.settings.os != 'Windows':
                cmake.definitions['WITH_NEON'] = 'ON'

        if self.settings.os == 'Windows':
            cmake.definitions['MSVC_RUNTIME'] = 'static'

        openssl_path = self.deps_cpp_info['openssl'].rootpath
        winpr_path = self.deps_cpp_info['winpr'].rootpath
        zlib_path = self.deps_cpp_info['zlib'].rootpath
        mbedtls_path = self.deps_cpp_info['mbedtls'].rootpath
        cmake.definitions['CMAKE_PREFIX_PATH'] = '%s;%s;%s;%s' % (openssl_path, winpr_path, zlib_path, mbedtls_path)

        cmake.definitions['MBEDTLS_LIB_DIR'] = os.path.join(mbedtls_path, "lib")
        cmake.definitions['OPENSSL_ROOT_DIR'] = openssl_path
        cmake.definitions['CMAKE_VERBOSE_MAKEFILE'] = 'ON'

        cmake.configure(source_folder=self.name)

        # conan doesn't support properly switching runtimes at the moment,
        # need to use this hack in the meantime
        if self.settings.os == 'Windows':
            tools.replace_in_file('CMakeCache.txt', '/MD', '/MT', strict=False)
            cmake.configure(source_folder=self.name)

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
            self.copy('*.dll', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)
            self.copy('*.so', dst='lib', keep_path=False)
            self.copy('*.dylib', dst='lib', keep_path=False)

        if self.settings.os == 'iOS' and self.settings.arch == 'universal':
            self.copy('*.h')
        else:
            self.copy('*.h', src='freerdp/include/freerdp', dst='include/freerdp') # CMAKE_SOURCE_DIR
            self.copy('*.h', src='include/freerdp', dst='include/freerdp') # CMAKE_BINARY_DIR

    def package_info(self):
        all_libs = tools.collect_libs(self)

        self.cpp_info.libs = ['']
        self.cpp_info.libs.append('freerdp-client2')

        for lib in all_libs:
            if lib.endswith('-client'):
                self.cpp_info.libs.append(lib)

        for lib in all_libs:
            if '-client-' in lib:
                self.cpp_info.libs.append(lib)

        self.cpp_info.libs.append('freerdp2')

        for lib in self.cpp_info.libs:
            print(lib)

        for lib in all_libs:
            if lib not in self.cpp_info.libs:
                self.cpp_info.libs.append(lib)

        if self.settings.compiler == 'Visual Studio' and self.settings.os == 'Windows':
            for lib in ['ws2_32', 'dbghelp', 'crypt32']:
                self.cpp_info.libs.append(lib)
        elif self.settings.os == 'Linux' or self.settings.os == 'Macos':
            for lib in ['pthread', 'm', 'dl', 'cups']:
                self.cpp_info.libs.append(lib)
        elif self.settings.os == 'Android':
            for lib in ['m', 'dl', 'log', 'OpenSLES']:
                self.cpp_info.libs.append(lib)
