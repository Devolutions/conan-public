from conans import ConanFile, CMake, tools, python_requires
import os

class WinprConan(ConanFile):
    name = 'winpr'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Apache 2.0'
    url = 'https://github.com/Devolutions/FreeRDP.git'
    description = 'FreeRDP is a free remote desktop protocol client'
    settings = 'os', 'arch', 'build_type'
    branch = 'devolutions-rdp2'
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

    def build_requirements(self):
        self.build_requires('mbedtls/2.16.0@devolutions/stable')
        self.build_requires('zlib/1.2.11@devolutions/stable')

    def source(self):
        if self.settings.arch == 'universal':
            return

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

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['ENABLE_TESTING'] = 'OFF'
        cmake.definitions['WINPR_ONLY'] = 'ON'
        cmake.definitions['WITH_WINPR_TOOLS'] = 'OFF'

        if self.settings.os == 'Linux':
            cmake.definitions['WITH_LIBSYSTEMD'] = 'OFF'

        if self.settings.os == 'Windows':
            cmake.definitions['MSVC_RUNTIME'] = 'static'

        mbedtls_path = self.deps_cpp_info['mbedtls'].rootpath
        zlib_path = self.deps_cpp_info['zlib'].rootpath
        cmake.definitions['CMAKE_PREFIX_PATH'] = '%s;%s' % (mbedtls_path, zlib_path)

        cmake.configure(source_folder=self.name)

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)

        if self.settings.arch == 'universal':
            self.copy('*.h')
        else:
            self.copy('*.h', src='winpr/winpr/include', dst='include')
            self.copy('*.h', src='winpr/include/winpr', dst='include/winpr')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == 'Windows':
            for lib in ['ws2_32', 'dbghelp', 'crypt32', 'shell32', 'shlwapi']:
                self.cpp_info.libs.append(lib)
        elif self.settings.os == 'Linux' or self.settings.os == 'Macos':
            for lib in ['pthread', 'm', 'dl']:
                self.cpp_info.libs.append(lib)
