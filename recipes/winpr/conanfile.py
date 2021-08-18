from conans import ConanFile, CMake, tools, python_requires
import os

lipo = python_requires('lipo/latest@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class WinprConan(ConanFile):
    name = 'winpr'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    license = 'Apache 2.0'
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

    def build(self):
        if self.settings.arch == 'universal' and self.settings.os == 'iOS':
            lipo.create(self, self.build_folder)
        else:
            cmake = CMake(self)
            utils.cmake_wrapper(cmake, self.settings, self.options)

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

            # conan doesn't support properly switching runtimes at the moment,
            # need to use this hack in the meantime
            if self.settings.os == 'Windows':
                tools.replace_in_file('CMakeCache.txt', '/MD', '/MT', strict=False)
                cmake.configure(source_folder=self.name)

            cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)

        if self.settings.os == 'iOS' and self.settings.arch == 'universal':
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
