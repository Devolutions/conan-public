from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, load, replace_in_file, save
from conan.tools.scm import Git
import os
import shutil


class FreerdpConan(ConanFile):
    name = "freerdp"
    exports = "VERSION", "FindWinPR.cmake"
    license = "Apache 2.0"
    no_copy_source = True
    url = "https://github.com/Devolutions/FreeRDP.git"
    description = "FreeRDP is a free remote desktop protocol client"
    settings = "os", "arch", "build_type"
    branch = "devolutions-rdp-3.26"
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()

    def requirements(self):
        self.requires("libressl/3.8.2@devolutions/stable")
        self.requires("winpr/3.0.0@devolutions/stable")
        self.requires("mbedtls/3.5.1@devolutions/stable")
        self.requires("zlib/1.3.1@devolutions/stable")
        self.requires("cjson/1.7.15@devolutions/stable")

        if self.settings.os in ("Windows", "Linux", "Macos"):
            self.requires("openh264/2.6.0@devolutions/stable")
            self.requires("libfido2/1.14.0@devolutions/stable")
            self.requires("libcbor/0.10.2@devolutions/stable")

            if self.settings.os == "Linux":
                self.requires("libpng/1.6.47@devolutions/stable")
                self.requires("libjpeg/3.1.0@devolutions/stable")

    def layout(self):
        cmake_layout(self)

    def source(self):
        folder = self.name

        if "CONAN_SOURCES_PATH" in os.environ:
            sources_path = os.path.join(os.environ["CONAN_SOURCES_PATH"], self.name)
            shutil.copytree(sources_path, os.path.join(self.source_folder, self.name))
        else:
            self.output.info(f"Cloning repo: {self.url} dest: {folder} branch: {self.branch}")
            git = Git(self)
            git.clone(url=self.url, target=folder, args=["--branch", self.branch])
            self.output.info(f"Current commit: {Git(self, folder=folder).get_commit()}")

        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "cmake", "FindMbedTLS.cmake"),
            "set(MBEDTLS_FOUND TRUE)",
            "set(MBEDTLS_FOUND TRUE)\n  set(MbedTLS_FOUND TRUE)",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "cmake", "FindOpenSSL.cmake"),
            "if (UNIX AND NOT ANDROID)",
            "if (UNIX AND NOT ANDROID AND NOT APPLE)",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "cmake", "FindOpenSSL.cmake"),
            'list(PREPEND CMAKE_FIND_ROOT_PATH "${OPENSSL_ROOT_DIR}")',
            'list(PREPEND CMAKE_FIND_ROOT_PATH "${OPENSSL_ROOT_DIR}")\n'
            '  set(OPENSSL_INCLUDE_DIR "${OPENSSL_ROOT_DIR}/include")\n'
            '  if(WIN32)\n'
            '    set(OPENSSL_SSL_LIBRARY "${OPENSSL_ROOT_DIR}/lib/libssl.lib")\n'
            '    set(OPENSSL_CRYPTO_LIBRARY "${OPENSSL_ROOT_DIR}/lib/libcrypto.lib")\n'
            '  else()\n'
            '    set(OPENSSL_SSL_LIBRARY "${OPENSSL_ROOT_DIR}/lib/libssl.a")\n'
            '    set(OPENSSL_CRYPTO_LIBRARY "${OPENSSL_ROOT_DIR}/lib/libcrypto.a")\n'
            '  endif()',
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "cmake", "FindOpenSSL.cmake"),
            "MARK_AS_ADVANCED(OPENSSL_INCLUDE_DIR OPENSSL_LIBRARIES OPENSSL_DEBUG_LIBRARIES OPENSSL_RELEASE_LIBRARIES)",
            "if(OPENSSL_ROOT_DIR)\n"
            "  set(OPENSSL_INCLUDE_DIR \"${OPENSSL_ROOT_DIR}/include\")\n"
            "  if(WIN32)\n"
            "    set(OPENSSL_SSL_LIBRARY \"${OPENSSL_ROOT_DIR}/lib/libssl.lib\")\n"
            "    set(OPENSSL_CRYPTO_LIBRARY \"${OPENSSL_ROOT_DIR}/lib/libcrypto.lib\")\n"
            "  else()\n"
            "    set(OPENSSL_SSL_LIBRARY \"${OPENSSL_ROOT_DIR}/lib/libssl.a\")\n"
            "    set(OPENSSL_CRYPTO_LIBRARY \"${OPENSSL_ROOT_DIR}/lib/libcrypto.a\")\n"
            "  endif()\n"
            "  set(OPENSSL_SSL_LIBRARIES ${OPENSSL_SSL_LIBRARY})\n"
            "  set(OPENSSL_CRYPTO_LIBRARIES ${OPENSSL_CRYPTO_LIBRARY})\n"
            "  set(OPENSSL_LIBRARIES ${OPENSSL_SSL_LIBRARY} ${OPENSSL_CRYPTO_LIBRARY})\n"
            "endif()\n"
            "MARK_AS_ADVANCED(OPENSSL_INCLUDE_DIR OPENSSL_LIBRARIES OPENSSL_DEBUG_LIBRARIES OPENSSL_RELEASE_LIBRARIES)",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "CMakeLists.txt"),
            "find_package(WinPR 3 REQUIRED)",
            "find_package(WinPR 3 REQUIRED MODULE)",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "CMakeLists.txt"),
            "  find_feature(OpenSSL ${OPENSSL_FEATURE_TYPE} ${OPENSSL_FEATURE_PURPOSE} ${OPENSSL_FEATURE_DESCRIPTION})",
            "  find_feature(OpenSSL ${OPENSSL_FEATURE_TYPE} ${OPENSSL_FEATURE_PURPOSE} ${OPENSSL_FEATURE_DESCRIPTION})\n"
            "  if(FREERDP_EXTERNAL_SSL_PATH)\n"
            "    set(_devolutions_openssl_root ${FREERDP_EXTERNAL_SSL_PATH})\n"
            "  elseif(IOS AND FREERDP_IOS_EXTERNAL_SSL_PATH)\n"
            "    set(_devolutions_openssl_root ${FREERDP_IOS_EXTERNAL_SSL_PATH})\n"
            "  elseif(OPENSSL_ROOT_DIR)\n"
            "    set(_devolutions_openssl_root ${OPENSSL_ROOT_DIR})\n"
            "  endif()\n"
            "  if(_devolutions_openssl_root)\n"
            "    set(OPENSSL_INCLUDE_DIR ${_devolutions_openssl_root}/include)\n"
            "    if(WIN32)\n"
            "      set(OPENSSL_SSL_LIBRARY ${_devolutions_openssl_root}/lib/libssl.lib)\n"
            "      set(OPENSSL_CRYPTO_LIBRARY ${_devolutions_openssl_root}/lib/libcrypto.lib)\n"
            "    else()\n"
            "      set(OPENSSL_SSL_LIBRARY ${_devolutions_openssl_root}/lib/libssl.a)\n"
            "      set(OPENSSL_CRYPTO_LIBRARY ${_devolutions_openssl_root}/lib/libcrypto.a)\n"
            "    endif()\n"
            "    set(OPENSSL_SSL_LIBRARIES ${OPENSSL_SSL_LIBRARY})\n"
            "    set(OPENSSL_CRYPTO_LIBRARIES ${OPENSSL_CRYPTO_LIBRARY})\n"
            "    set(OPENSSL_LIBRARIES ${OPENSSL_SSL_LIBRARY} ${OPENSSL_CRYPTO_LIBRARY})\n"
            "  endif()",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "DevolutionsRdp", "CMakeLists.txt"),
            "add_library(${MODULE_NAME} ${TARGET_TYPE} ${${MODULE_PREFIX}_HEADERS} ${${MODULE_PREFIX}_SOURCES} ${${MODULE_PREFIX}_RESOURCES})",
            "add_library(${MODULE_NAME} ${TARGET_TYPE} ${${MODULE_PREFIX}_HEADERS} ${${MODULE_PREFIX}_SOURCES} ${${MODULE_PREFIX}_RESOURCES})\n"
            "target_include_directories(${MODULE_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "DevolutionsRdp", "CMakeLists.txt"),
            "target_link_libraries(${MODULE_NAME} PRIVATE freerdp freerdp-client winpr)",
            "target_link_libraries(${MODULE_NAME} PRIVATE freerdp freerdp-client winpr)\n"
            "if(MBEDTLS_LIBRARY)\n"
            "    target_link_libraries(${MODULE_NAME} PRIVATE ${MBEDTLS_LIBRARY} ${MBEDX509_LIBRARY} ${MBEDCRYPTO_LIBRARY})\n"
            "endif()",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "DevolutionsRdp", "channel_stub.c"),
            "#include <winpr/wtypes.h>",
            "#include <winpr/wtypes.h>\n#include <winpr/wtsapi.h>",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "DevolutionsRdp", "channel_stub.c"),
            "extern unsigned int rdpewa_DVCPluginEntry(void* pEntryPoints);",
            "extern unsigned int VCAPITYPE rdpewa_DVCPluginEntry(void* pEntryPoints);",
        )

        with open(os.path.join(self.source_folder, folder, "CMakeLists.txt"), "a", encoding="utf-8") as file:
            file.write("\nadd_subdirectory(DevolutionsRdp)\n")

    def generate(self):
        copy(self, "FindWinPR.cmake", src=self.recipe_folder, dst=self.generators_folder)

        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["CMAKE_MODULE_PATH"] = self._cmake_path(self.generators_folder)
        tc.variables["FREERDP_UNIFIED_BUILD"] = False
        tc.variables["WITH_FREERDP_DEPRECATED"] = False
        tc.variables["WITH_CLIENT_COMMON"] = True
        tc.variables["WITH_CLIENT"] = False
        tc.variables["WITH_SERVER"] = False
        tc.variables["WITH_WAYLAND"] = False
        tc.variables["WITH_X11"] = False
        tc.variables["WITH_MANPAGES"] = False
        tc.variables["WITH_FFMPEG"] = False
        tc.variables["WITH_VAAPI"] = False
        tc.variables["WITH_VAAPI_H264_ENCODING"] = False
        tc.variables["WITH_GSTREAMER_1_0"] = False
        tc.variables["WITH_GSTREAMER_0_10"] = False
        tc.variables["WITH_LIBSYSTEMD"] = False
        tc.variables["WITH_OPENSSL"] = True
        tc.variables["WITH_MBEDTLS"] = True
        tc.variables["WITH_ALSA"] = False
        tc.variables["WITH_OSS"] = False
        tc.variables["WITH_FUSE"] = False
        tc.variables["CHANNEL_URBDRC"] = False

        if self.settings.os != "Linux":
            tc.variables["WITH_SWSCALE"] = False

        if self.settings.os == "Linux":
            tc.variables["WITH_CUPS"] = True
            tc.variables["WITH_ALSA"] = True
            tc.variables["WITH_INTERPROCEDURAL_OPTIMIZATION"] = False
            tc.variables["WITH_SWSCALE"] = True
            tc.variables["WITH_SWSCALE_LOADING"] = True
            tc.variables["CHANNEL_RDPECAM_CLIENT"] = True
            jpeg_path = self._package_path("libjpeg")
            png_path = self._package_path("libpng")
            tc.variables["JPEG_LIBRARY"] = f"{jpeg_path}/lib/libturbojpeg.a"
            tc.variables["PNG_LIBRARY"] = f"{png_path}/lib/libpng.a"

        if self.settings.os == "Macos":
            tc.variables["WITH_CUPS"] = True
            tc.variables["WITH_OPUS"] = False
            tc.variables["WITH_MACAUDIO"] = True

        if self.settings.os == "iOS":
            tc.variables["WITH_IOSAUDIO"] = True

        if self.settings.arch in ("x86", "x86_64"):
            tc.variables["WITH_SSE2"] = True
        else:
            tc.variables["WITH_SSE2"] = False
            if self.settings.os != "Windows":
                tc.variables["WITH_NEON"] = True

        if self.settings.os == "Windows":
            tc.variables["CMAKE_SYSTEM_VERSION"] = "10.0.19041.0"
            tc.variables["MSVC_RUNTIME"] = "static"
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"
            tc.preprocessor_definitions["WINVER"] = "0x0601"
            tc.preprocessor_definitions["_WIN32_WINNT"] = "0x0601"

        if self.settings.os == "Android" and self.settings.arch == "armv7":
            tc.variables["WITH_INTERPROCEDURAL_OPTIMIZATION"] = False

        if self.settings.build_type == "Debug":
            tc.variables["WITH_INTERPROCEDURAL_OPTIMIZATION"] = False
            tc.variables["WITH_DEBUG_CAPABILITIES"] = True
            tc.variables["WITH_DEBUG_CHANNELS"] = True
            tc.variables["WITH_DEBUG_CLIPRDR"] = True
            tc.variables["WITH_DEBUG_CODECS"] = True
            tc.variables["WITH_DEBUG_RDPGFX"] = True
            tc.variables["WITH_DEBUG_DVC"] = True
            tc.variables["WITH_DEBUG_TSMF"] = True
            tc.variables["WITH_DEBUG_KBD"] = True
            tc.variables["WITH_DEBUG_LICENSE"] = True
            tc.variables["WITH_DEBUG_NEGO"] = True
            tc.variables["WITH_DEBUG_NLA"] = True
            tc.variables["WITH_DEBUG_TSG"] = True
            tc.variables["WITH_DEBUG_RDP"] = True
            tc.variables["WITH_DEBUG_RDPEI"] = True
            tc.variables["WITH_DEBUG_REDIR"] = True
            tc.variables["WITH_DEBUG_RDPDR"] = True
            tc.variables["WITH_DEBUG_RFX"] = True
            tc.variables["WITH_DEBUG_SCARD"] = True
            tc.variables["WITH_DEBUG_SND"] = True
            tc.variables["WITH_DEBUG_SVC"] = True
            tc.variables["WITH_DEBUG_TRANSPORT"] = True
            tc.variables["WITH_DEBUG_TIMEZONE"] = True

        openssl_path = self._package_path("libressl")
        winpr_path = self._package_path("winpr")
        zlib_path = self._package_path("zlib")
        mbedtls_path = self._package_path("mbedtls")
        cjson_path = self._package_path("cjson")
        tc.variables["FREERDP_EXTERNAL_SSL_PATH"] = openssl_path
        tc.variables["FREERDP_IOS_EXTERNAL_SSL_PATH"] = openssl_path
        tc.variables["OPENSSL_ROOT_DIR"] = openssl_path
        tc.variables["OPENSSL_USE_STATIC_LIBS"] = True
        tc.variables["OPENSSL_INCLUDE_DIR"] = f"{openssl_path}/include"
        openssl_ssl_library = f"{openssl_path}/lib/libssl.lib" if self.settings.os == "Windows" else f"{openssl_path}/lib/libssl.a"
        openssl_crypto_library = f"{openssl_path}/lib/libcrypto.lib" if self.settings.os == "Windows" else f"{openssl_path}/lib/libcrypto.a"
        tc.variables["OPENSSL_SSL_LIBRARY"] = openssl_ssl_library
        tc.variables["OPENSSL_CRYPTO_LIBRARY"] = openssl_crypto_library
        tc.variables["OPENSSL_SSL_LIBRARIES"] = openssl_ssl_library
        tc.variables["OPENSSL_CRYPTO_LIBRARIES"] = openssl_crypto_library
        tc.variables["OPENSSL_LIBRARIES"] = ";".join([openssl_ssl_library, openssl_crypto_library])
        self._force_openssl_toolchain(tc, openssl_path, openssl_ssl_library, openssl_crypto_library)
        tc.variables["MBEDTLS_ROOT"] = mbedtls_path
        tc.variables["MBEDTLS_FOUND"] = True
        tc.variables["MbedTLS_FOUND"] = True
        tc.variables["MBEDTLS_INCLUDE_DIR"] = f"{mbedtls_path}/include"
        mbedtls_lib = f"{mbedtls_path}/lib/mbedtls.lib" if self.settings.os == "Windows" else f"{mbedtls_path}/lib/libmbedtls.a"
        mbedcrypto_lib = f"{mbedtls_path}/lib/mbedcrypto.lib" if self.settings.os == "Windows" else f"{mbedtls_path}/lib/libmbedcrypto.a"
        mbedx509_lib = f"{mbedtls_path}/lib/mbedx509.lib" if self.settings.os == "Windows" else f"{mbedtls_path}/lib/libmbedx509.a"
        tc.variables["MBEDTLS_LIBRARY"] = mbedtls_lib
        tc.variables["MBEDCRYPTO_LIBRARY"] = mbedcrypto_lib
        tc.variables["MBEDX509_LIBRARY"] = mbedx509_lib
        tc.variables["MBEDTLS_LIBRARIES"] = ";".join([mbedtls_lib, mbedcrypto_lib, mbedx509_lib])
        tc.variables["WinPR_INCLUDE_DIR"] = f"{winpr_path}/include"
        tc.variables["WinPR_LIBRARY"] = f"{winpr_path}/lib/winpr3.lib" if self.settings.os == "Windows" else f"{winpr_path}/lib/libwinpr3.a"
        tc.variables["cJSON_LIBRARY"] = f"{cjson_path}/lib/cjson.lib" if self.settings.os == "Windows" else f"{cjson_path}/lib/libcjson.a"
        tc.variables["CMAKE_PREFIX_PATH"] = ";".join([openssl_path, winpr_path, zlib_path, mbedtls_path, cjson_path])
        tc.variables["CMAKE_VERBOSE_MAKEFILE"] = True

        if self.settings.os in ("Windows", "Linux", "Macos"):
            openh264_path = self._package_path("openh264")
            openh264_version = str(self.dependencies["openh264"].ref.version)
            tc.variables["OPENH264_LIBRARY"] = f"{openh264_path}/lib/{self.openh264_filename(openh264_version)}"
            tc.variables["OPENH264_INCLUDE_DIR"] = f"{openh264_path}/include"
            tc.variables["WITH_OPENH264"] = True
            tc.variables["WITH_OPENH264_LOADING"] = True

            libfido2_path = self._package_path("libfido2")
            libcbor_path = self._package_path("libcbor")
            fido2_lib = "fido2.lib" if self.settings.os == "Windows" else "libfido2.a"
            cbor_lib = "cbor.lib" if self.settings.os == "Windows" else "libcbor.a"
            tc.variables["LIBFIDO2_INCLUDE_DIR"] = f"{libfido2_path}/include"
            libfido2_library = f"{libfido2_path}/lib/{fido2_lib}"
            if self.settings.os == "Macos":
                libfido2_library = ";".join([libfido2_library, openssl_crypto_library])
            tc.variables["LIBFIDO2_LIBRARY"] = libfido2_library
            tc.variables["LIBCBOR_INCLUDE_DIR"] = f"{libcbor_path}/include"
            tc.variables["LIBCBOR_LIBRARY"] = f"{libcbor_path}/lib/{cbor_lib}"
            tc.variables["CHANNEL_RDPEWA"] = True

        if self.settings.os == "Android":
            tc.variables["WITH_MEDIACODEC"] = True

        tc.generate()

    def build(self):
        if str(self.settings.arch) == "universal":
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()

    def package(self):
        if self.settings.os == "Windows":
            copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.pdb", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        else:
            copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

        if self.settings.os == "iOS" and str(self.settings.arch) == "universal":
            copy(self, "*.h", src=self.source_folder, dst=self.package_folder, keep_path=True)
        else:
            copy(self, "*.h", src=os.path.join(self.source_folder, "freerdp", "include", "freerdp"), dst=os.path.join(self.package_folder, "include", "freerdp"), keep_path=True)
            copy(self, "*.h", src=os.path.join(self.build_folder, "include", "freerdp"), dst=os.path.join(self.package_folder, "include", "freerdp"), keep_path=True)

    def package_info(self):
        all_libs = collect_libs(self)

        ordered_libs = []
        for preferred in ("freerdp-client3", "freerdp3"):
            if preferred in all_libs:
                ordered_libs.append(preferred)

        for lib in all_libs:
            if lib not in ordered_libs:
                ordered_libs.append(lib)

        self.cpp_info.libs = ordered_libs

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "dbghelp", "crypt32", "setupapi", "hid"])
        elif self.settings.os in ("Linux", "Macos"):
            self.cpp_info.system_libs.extend(["pthread", "m", "dl", "cups"])
            if self.settings.os == "Macos":
                self.cpp_info.frameworks = ["IOKit", "CoreFoundation"]
        elif self.settings.os == "Android":
            self.cpp_info.system_libs.extend(["m", "dl", "log", "OpenSLES"])

    def _package_path(self, name):
        return self.dependencies[name].package_folder.replace("\\", "/")

    def _force_openssl_toolchain(self, toolchain, openssl_path, openssl_ssl_library, openssl_crypto_library):
        wrapper = os.path.join(self.generators_folder, "devolutions_openssl.cmake").replace("\\", "/")
        save(
            self,
            wrapper,
            "\n".join(
                [
                    f'set(OPENSSL_ROOT_DIR "{openssl_path}" CACHE PATH "" FORCE)',
                    f'set(OPENSSL_INCLUDE_DIR "{openssl_path}/include" CACHE PATH "" FORCE)',
                    f'set(OPENSSL_SSL_LIBRARY "{openssl_ssl_library}" CACHE FILEPATH "" FORCE)',
                    f'set(OPENSSL_CRYPTO_LIBRARY "{openssl_crypto_library}" CACHE FILEPATH "" FORCE)',
                    f'set(OPENSSL_SSL_LIBRARIES "{openssl_ssl_library}" CACHE STRING "" FORCE)',
                    f'set(OPENSSL_CRYPTO_LIBRARIES "{openssl_crypto_library}" CACHE STRING "" FORCE)',
                    f'set(OPENSSL_LIBRARIES "{openssl_ssl_library};{openssl_crypto_library}" CACHE STRING "" FORCE)',
                    "",
                ]
            ),
        )

        user_toolchain_block = toolchain.blocks["user_toolchain"]
        values = user_toolchain_block.values or {"paths": []}
        paths = [wrapper] + list(values.get("paths") or [])
        user_toolchain_block.values = {"paths": paths}

    @staticmethod
    def _cmake_path(path):
        return path.replace("\\", "/")
