from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os, shutil

class FreerdpConan(ConanFile):
    name = 'freerdp'
    exports = ['VERSION', 'FindWinPR.cmake']
    
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Apache 2.0'
    no_copy_source = True
    url = 'https://github.com/Devolutions/FreeRDP.git'
    description = 'FreeRDP is a free remote desktop protocol client'
    settings = 'os', 'arch', 'distro', 'build_type'
    branch = 'devolutions-rdp-rebase-20250616'
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

    def build_requirements(self):
        super().build_requirements()
        self.tool_requires('libressl/[3.8.2]@devolutions/stable')
        self.tool_requires('winpr/[3.0.0]@devolutions/stable')
        self.tool_requires('mbedtls/[3.5.1]@devolutions/stable')
        self.tool_requires('zlib/[1.3.1]@devolutions/stable')
        self.tool_requires('cjson/[1.7.15]@devolutions/stable')

        if self.settings.os in ["Windows", "Linux", "Macos"]:
            self.tool_requires('openh264/[2.6.0]@devolutions/stable')

            if self.settings.os == "Linux":
                self.tool_requires('libpng/[1.6.39]@devolutions/stable')
                self.tool_requires('libjpeg/[3.1.0]@devolutions/stable')

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name

        if 'CONAN_SOURCES_PATH' in os.environ:
            conan_sources_path = os.environ['CONAN_SOURCES_PATH']
            sources_path = os.path.join(conan_sources_path, self.name)
            shutil.copytree(sources_path, self.name)
        else:
            self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
            git = Git(self, folder=folder)
            git.clone(url=self.url, target=".")
            git.checkout(self.branch)
            self.output.info("Current commit: %s" % (git.get_commit()))

        with open(os.path.join(folder, "CMakeLists.txt"), 'a') as file:
            file.write('\nadd_subdirectory(DevolutionsRdp)')

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        # Deploy FindWinPR.cmake to build directory and adjust CMAKE_MODULE_PATH so it can be found
        shutil.copy(os.path.join(self.recipe_folder, "FindWinPR.cmake"), dst=self.build_folder)
        cmake.definitions['CMAKE_MODULE_PATH'] = self.build_folder.replace('\', '/')

        cmake.definitions['FREERDP_UNIFIED_BUILD'] = 'OFF'
        cmake.definitions['WITH_FREERDP_DEPRECATED'] = 'OFF'
        cmake.definitions['WITH_CLIENT_COMMON'] = 'ON'
        cmake.definitions['WITH_CLIENT'] = 'OFF'
        cmake.definitions['WITH_SERVER'] = 'OFF'
        cmake.definitions['WITH_WAYLAND'] = 'OFF'
        cmake.definitions['WITH_MANPAGES'] = 'OFF'
        cmake.definitions['WITH_FFMPEG'] = 'OFF'
        cmake.definitions['WITH_SWSCALE'] = 'OFF'
        cmake.definitions['WITH_VAAPI'] = 'OFF'
        cmake.definitions['WITH_GSTREAMER_1_0'] = 'OFF'
        cmake.definitions['WITH_GSTREAMER_0_10'] = 'OFF'
        cmake.definitions['WITH_LIBSYSTEMD'] = 'OFF'
        cmake.definitions['WITH_OPENSSL'] = 'ON'
        cmake.definitions['WITH_MBEDTLS'] = 'ON'
        cmake.definitions['WITH_ALSA'] = 'OFF'
        cmake.definitions['WITH_FUSE'] = 'OFF'
        cmake.definitions['CHANNEL_URBDRC'] = 'OFF'

        if self.settings.os == 'Linux':
            cmake.definitions['WITH_CUPS'] = 'ON'
            cmake.definitions['WITH_ALSA'] = 'ON'
            
        if self.settings.os == "Macos":
            cmake.definitions['WITH_CUPS'] = 'ON'
            cmake.definitions['WITH_OPUS'] = 'OFF'
            cmake.definitions['WITH_MACAUDIO'] = 'ON'

        if self.settings.os == "iOS":
            cmake.definitions['WITH_IOSAUDIO'] = 'ON'

        if self.settings.arch in ['x86', 'x86_64']:
            cmake.definitions['WITH_SSE2'] = 'ON'
        else:
            cmake.definitions['WITH_SSE2'] = 'OFF'
            if self.settings.os != 'Windows':
                cmake.definitions['WITH_NEON'] = 'ON'

        if self.settings.os == 'Windows':
            cmake.definitions['CMAKE_SYSTEM_VERSION'] = '10.0.19041.0'
            cmake.definitions['MSVC_RUNTIME'] = 'static'

        # Disable IPO
        if self.settings.os == 'Linux' or (self.settings.os == 'Android' and self.settings.arch == 'armv7'):
            cmake.definitions['WITH_INTERPROCEDURAL_OPTIMIZATION'] = 'OFF' # Currently not working in cbake

        if self.settings.os == 'Android' and self.settings.arch == 'armv7':
            cmake.definitions['WITH_INTERPROCEDURAL_OPTIMIZATION'] = 'OFF' # IPO doesn't seem to work on android-arm7

        # Debug builds
        if self.settings.build_type == 'Debug':
            cmake.definitions['WITH_INTERPROCEDURAL_OPTIMIZATION'] = 'OFF'
            cmake.definitions['WITH_DEBUG_CAPABILITIES'] = 'ON'
            cmake.definitions['WITH_DEBUG_CHANNELS'] = 'ON'
            cmake.definitions['WITH_DEBUG_CLIPRDR'] = 'ON'
            cmake.definitions['WITH_DEBUG_CODECS'] = 'ON'
            cmake.definitions['WITH_DEBUG_RDPGFX'] = 'ON'
            cmake.definitions['WITH_DEBUG_DVC'] = 'ON'
            cmake.definitions['WITH_DEBUG_TSMF'] = 'ON'
            cmake.definitions['WITH_DEBUG_KBD'] = 'ON'
            cmake.definitions['WITH_DEBUG_LICENSE'] = 'ON'
            cmake.definitions['WITH_DEBUG_NEGO'] = 'ON'
            cmake.definitions['WITH_DEBUG_NLA'] = 'ON'
            cmake.definitions['WITH_DEBUG_TSG'] = 'ON'
            cmake.definitions['WITH_DEBUG_RDP'] = 'ON'
            cmake.definitions['WITH_DEBUG_RDPEI'] = 'ON'
            cmake.definitions['WITH_DEBUG_REDIR'] = 'ON'
            cmake.definitions['WITH_DEBUG_RDPDR'] = 'ON'
            cmake.definitions['WITH_DEBUG_RFX'] = 'ON'
            cmake.definitions['WITH_DEBUG_SCARD'] = 'ON'
            cmake.definitions['WITH_DEBUG_SND'] = 'ON'
            cmake.definitions['WITH_DEBUG_SVC'] = 'ON'
            cmake.definitions['WITH_DEBUG_TRANSPORT'] = 'ON'
            cmake.definitions['WITH_DEBUG_TIMEZONE'] = 'ON'

        openssl_path = self.dependencies['libressl'].package_folder
        winpr_path = self.dependencies['winpr'].package_folder
        zlib_path = self.dependencies['zlib'].package_folder
        mbedtls_path = self.dependencies['mbedtls'].package_folder
        cjson_path = self.dependencies['cjson'].package_folder
        cmake.definitions['OPENSSL_ROOT_DIR'] = openssl_path
        cmake.definitions['CMAKE_PREFIX_PATH'] = '%s;%s;%s;%s;%s' % (openssl_path, winpr_path, zlib_path, mbedtls_path, cjson_path)
        cmake.definitions['CMAKE_VERBOSE_MAKEFILE'] = 'ON'

        if self.settings.os == "Linux":
            jpeg_path = self.dependencies['libjpeg'].package_folder
            cmake.definitions["JPEG_LIBRARY"] = os.path.join(jpeg_path, "lib", 'libturbojpeg.a')
            png_path = self.dependencies['libpng'].package_folder
            cmake.definitions["PNG_LIBRARY"] = os.path.join(png_path, "lib", 'libpng.a')

        if self.settings.os in ["Windows", "Linux", "Macos"]:
            openh264_path = self.dependencies['openh264'].package_folder
            cmake.definitions["OPENH264_LIBRARY"] = os.path.join(openh264_path, "lib", self.openh264_filename(self.deps_user_info["openh264"].version))
            cmake.definitions["OPENH264_INCLUDE_DIR"] = os.path.join(openh264_path, "include")
            cmake.definitions['WITH_OPENH264'] = 'ON'
            cmake.definitions['WITH_OPENH264_LOADING'] = 'ON'

        if self.settings.os == "Android":
            cmake.definitions['WITH_MEDIACODEC'] = 'ON'

        cmake.configure()

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            copy(self, '*.lib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
            copy(self, '*.dll', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
            copy(self, '*.pdb', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        else:
            copy(self, '*.a', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
            copy(self, '*.so', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
            copy(self, '*.dylib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)

        if self.settings.os == 'iOS' and self.settings.arch == 'universal':
            copy(self, '*.h')
        else:
            copy(self, '*.h', src=os.path.join(self.source_folder, 'freerdp/include/freerdp', dst=self.package_folder, src=self.build_folder), dst=os.path.join(self.package_folder, 'include/freerdp')) # CMAKE_SOURCE_DIR
            copy(self, '*.h', src=os.path.join(self.source_folder, 'include/freerdp'), dst=os.path.join(self.package_folder, 'include/freerdp')) # CMAKE_BINARY_DIR

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

        if self.settings.os == 'Windows':
            for lib in ['ws2_32', 'dbghelp', 'crypt32']:
                self.cpp_info.libs.append(lib)
        elif self.settings.os == 'Linux' or self.settings.os == 'Macos':
            for lib in ['pthread', 'm', 'dl', 'cups']:
                self.cpp_info.libs.append(lib)
        elif self.settings.os == 'Android':
            for lib in ['m', 'dl', 'log', 'OpenSLES']:
                self.cpp_info.libs.append(lib)
