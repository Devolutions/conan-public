from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, load, replace_in_file
from conan.tools.scm import Git
import os
import shutil


class WinprConan(ConanFile):
    name = "winpr"
    exports = "VERSION"
    license = "Apache 2.0"
    url = "https://github.com/Devolutions/FreeRDP.git"
    description = "FreeRDP is a free remote desktop protocol client"
    settings = "os", "arch", "build_type"
    branch = "devolutions-rdp-3.29"
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
        self.requires("mbedtls/3.5.1@devolutions/stable")
        self.requires("zlib/1.3.1@devolutions/stable")
        self.requires("libjpeg/3.1.0@devolutions/stable")
        self.requires("libpng/1.6.47@devolutions/stable")
        self.requires("cjson/1.7.15@devolutions/stable")

    def layout(self):
        cmake_layout(self)

    def source(self):
        folder = "freerdp"

        if "CONAN_SOURCES_PATH" in os.environ:
            sources_path = os.path.join(os.environ["CONAN_SOURCES_PATH"], folder)
            shutil.copytree(sources_path, os.path.join(self.source_folder, folder))
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

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["WITH_WINPR_DEPRECATED"] = False
        tc.variables["WITH_WINPR_TOOLS"] = False
        tc.variables["WITH_MBEDTLS"] = True
        tc.variables["WITH_OPENSSL"] = False
        tc.variables["WITH_INTERNAL_RC4"] = True
        tc.variables["WITH_INTERNAL_MD4"] = True
        tc.variables["WITH_INTERNAL_MD5"] = True

        if self.settings.os == "Linux":
            tc.variables["WINPR_UTILS_IMAGE_PNG"] = True
            tc.variables["WINPR_UTILS_IMAGE_JPEG"] = True
            tc.variables["WITH_LIBSYSTEMD"] = False
            tc.variables["WITH_UNICODE_BUILTIN"] = True
            tc.variables["WITH_KRB5"] = False
            tc.variables["WITH_PKCS11"] = False
            tc.variables["WITH_INTERPROCEDURAL_OPTIMIZATION"] = False
            tc.variables["JPEG_LIBRARY"] = f"{self._package_path('libjpeg')}/lib/libturbojpeg.a"
            tc.variables["JPEG_INCLUDE_DIR"] = f"{self._package_path('libjpeg')}/include"
            tc.variables["PNG_LIBRARY"] = f"{self._package_path('libpng')}/lib/libpng.a"
            tc.variables["PNG_INCLUDE_DIR"] = f"{self._package_path('libpng')}/include"

        if self.settings.os == "Macos":
            tc.variables["WITH_PKCS11"] = True

        if self.settings.os == "Windows":
            tc.variables["CMAKE_SYSTEM_VERSION"] = "10.0.19041.0"
            tc.variables["MSVC_RUNTIME"] = "static"
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"
            tc.variables["WITH_JSON_DISABLED"] = True
            tc.preprocessor_definitions["WINVER"] = "0x0601"
            tc.preprocessor_definitions["_WIN32_WINNT"] = "0x0601"

        mbedtls_path = self._package_path("mbedtls")
        zlib_path = self._package_path("zlib")
        cjson_path = self._package_path("cjson")
        tc.variables["MBEDTLS_ROOT"] = mbedtls_path
        tc.variables["MBEDTLS_FOUND"] = True
        tc.variables["MbedTLS_FOUND"] = True
        tc.variables["MBEDTLS_INCLUDE_DIR"] = f"{mbedtls_path}/include"
        tc.variables["MBEDTLS_LIBRARY"] = f"{mbedtls_path}/lib/mbedtls.lib" if self.settings.os == "Windows" else f"{mbedtls_path}/lib/libmbedtls.a"
        tc.variables["MBEDCRYPTO_LIBRARY"] = f"{mbedtls_path}/lib/mbedcrypto.lib" if self.settings.os == "Windows" else f"{mbedtls_path}/lib/libmbedcrypto.a"
        tc.variables["MBEDX509_LIBRARY"] = f"{mbedtls_path}/lib/mbedx509.lib" if self.settings.os == "Windows" else f"{mbedtls_path}/lib/libmbedx509.a"
        tc.variables["ZLIB_ROOT"] = zlib_path
        if self.settings.os == "Macos":
            tc.variables["CMAKE_PREFIX_PATH"] = ";".join([mbedtls_path, zlib_path, cjson_path])
        else:
            tc.variables["CMAKE_PREFIX_PATH"] = ";".join([mbedtls_path, zlib_path])

        if self.settings.os == "Android":
            tc.variables["CMAKE_FIND_ROOT_PATH"] = ";".join([mbedtls_path, zlib_path])
            if self.settings.arch == "armv7":
                tc.variables["WITH_INTERPROCEDURAL_OPTIMIZATION"] = False

        if self.settings.build_type == "Debug":
            tc.variables["WITH_INTERPROCEDURAL_OPTIMIZATION"] = False

        tc.generate()

    def build(self):
        if str(self.settings.arch) == "universal":
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "freerdp", self.name))
        cmake.build()

    def package(self):
        if self.settings.os == "Windows":
            copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        else:
            copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

        if str(self.settings.arch) == "universal":
            copy(self, "*.h", src=self.source_folder, dst=self.package_folder, keep_path=True)
        else:
            copy(self, "config.h", src=self.build_folder, dst=os.path.join(self.package_folder, "include", "winpr"), keep_path=False)
            copy(self, "*.h", src=os.path.join(self.build_folder, "include", "winpr"), dst=os.path.join(self.package_folder, "include", "winpr"), keep_path=True)
            copy(self, "*.h", src=os.path.join(self.source_folder, "freerdp", "winpr", "include", "winpr"), dst=os.path.join(self.package_folder, "include", "winpr"), keep_path=True)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "dbghelp", "crypt32", "shell32", "shlwapi"])
        elif self.settings.os in ("Linux", "Macos"):
            self.cpp_info.system_libs.extend(["pthread", "m", "dl"])
        elif self.settings.os == "iOS":
            for lib in ["Foundation", "CoreFoundation"]:
                self.cpp_info.exelinkflags.append(f"-framework {lib}")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags

    def _package_path(self, name):
        return self.dependencies[name].package_folder.replace("\\", "/")
