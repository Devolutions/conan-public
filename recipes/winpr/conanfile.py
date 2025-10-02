from conans import ConanFile, CMake, tools, python_requires
import os, shutil

class WinprConan(ConanFile):
    name = 'winpr'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Apache 2.0'
    url = 'https://github.com/Devolutions/FreeRDP.git'
    description = 'FreeRDP is a free remote desktop protocol client'
    settings = 'os', 'arch', 'distro', 'build_type'
    branch = 'devolutions-rdp-rebase-20250616'
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
        super().build_requirements()
        self.build_requires('mbedtls/3.5.1@devolutions/stable')
        self.build_requires('zlib/1.3.1@devolutions/stable')
        self.build_requires('libjpeg/3.1.0@devolutions/stable')
        self.build_requires('libpng/1.6.47@devolutions/stable')

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = 'freerdp'

        if 'CONAN_SOURCES_PATH' in os.environ:
            conan_sources_path = os.environ['CONAN_SOURCES_PATH']
            sources_path = os.path.join(conan_sources_path, folder)
            shutil.copytree(sources_path, folder)
        else:
            self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
            git = tools.Git(folder=folder)
            git.clone(self.url)
            git.checkout(self.branch)
            self.output.info("Current commit: %s" % (git.get_commit()))

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['WITH_WINPR_DEPRECATED'] = 'OFF'
        cmake.definitions['WITH_WINPR_TOOLS'] = 'OFF'
        cmake.definitions['WITH_MBEDTLS'] = 'ON'
        cmake.definitions['WITH_OPENSSL'] = 'OFF'

        cmake.definitions['WITH_INTERNAL_RC4'] = 'ON'
        cmake.definitions['WITH_INTERNAL_MD4'] = 'ON'
        cmake.definitions['WITH_INTERNAL_MD5'] = 'ON'

        if self.settings.os in ["Linux"]:
            cmake.definitions['WINPR_UTILS_IMAGE_PNG'] = 'ON'
            cmake.definitions['WINPR_UTILS_IMAGE_JPEG'] = 'ON'

            if self.settings.os == 'Linux':
                jpeg_path = self.deps_cpp_info['libjpeg'].rootpath
                cmake.definitions["JPEG_LIBRARY"] = os.path.join(jpeg_path, self.deps_cpp_info['libjpeg'].libdirs[0], 'libturbojpeg.a')
                cmake.definitions["JPEG_INCLUDE_DIR"] = os.path.join(jpeg_path, self.deps_cpp_info['libjpeg'].includedirs[0])

                png_path = self.deps_cpp_info['libpng'].rootpath
                cmake.definitions["PNG_LIBRARY"] = os.path.join(png_path, self.deps_cpp_info['libpng'].libdirs[0], 'libpng.a')
                cmake.definitions["PNG_INCLUDE_DIR"] = os.path.join(png_path, self.deps_cpp_info['libpng'].includedirs[0])

        if self.settings.os == "Macos":
            cmake.definitions['WITH_PKCS11'] = 'OFF'

        if self.settings.os == 'Linux':
            cmake.definitions['WITH_LIBSYSTEMD'] = 'OFF'
            cmake.definitions['WITH_UNICODE_BUILTIN'] = 'ON'
            cmake.definitions['WITH_KRB5'] = 'OFF'
            cmake.definitions['WITH_PKCS11'] = 'OFF'

        if self.settings.os == 'Windows':
            cmake.definitions['CMAKE_SYSTEM_VERSION'] = '10.0.19041.0'
            cmake.definitions['MSVC_RUNTIME'] = 'static'

        mbedtls_path = self.deps_cpp_info['mbedtls'].rootpath
        zlib_path = self.deps_cpp_info['zlib'].rootpath
        cmake.definitions['CMAKE_PREFIX_PATH'] = '%s;%s' % (mbedtls_path, zlib_path)
        
        if self.settings.os == 'Android': # Android toolchain overwrites CMAKE_PREFIX_PATH
            cmake.definitions['CMAKE_FIND_ROOT_PATH'] = '%s;%s' % (mbedtls_path, zlib_path)
            
        # Disable IPO
        if self.settings.os == 'Linux':
            cmake.definitions['WITH_INTERPROCEDURAL_OPTIMIZATION'] = 'OFF' # Currently not working in cbake

        if self.settings.os == 'Android' and self.settings.arch == 'armv7':
            cmake.definitions['WITH_INTERPROCEDURAL_OPTIMIZATION'] = 'OFF' # IPO doesn't seem to work on android-arm7

        # Debug builds
        if self.settings.build_type == 'Debug':
            cmake.definitions['WITH_INTERPROCEDURAL_OPTIMIZATION'] = 'OFF'

        cmake.configure(source_folder=os.path.join('freerdp', self.name))

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)

        if self.settings.arch == 'universal':
            self.copy('*.h')
        else:
            self.copy('config.h', dst='include/winpr')
            self.copy('*.h', src='include/winpr', dst='include/winpr')
            self.copy('*.h', src='freerdp/winpr/include/winpr', dst='include/winpr')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == 'Windows':
            for lib in ['ws2_32', 'dbghelp', 'crypt32', 'shell32', 'shlwapi']:
                self.cpp_info.libs.append(lib)
        elif self.settings.os == 'Linux' or self.settings.os == 'Macos':
            for lib in ['pthread', 'm', 'dl']:
                self.cpp_info.libs.append(lib)
        elif self.settings.os == 'iOS':
            for lib in ['Foundation', 'CoreFoundation']:
              self.cpp_info.exelinkflags.append('-framework %s' % lib)
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
