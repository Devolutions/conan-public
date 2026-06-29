from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, load, patch, replace_in_file
from conan.tools.scm import Git
import os


class MbedtlsConan(ConanFile):
    name = "mbedtls"
    exports = "VERSION", "patches/*"
    license = "Apache 2.0"
    url = "https://github.com/Mbed-TLS/mbedtls"
    description = "An open source, portable, easy to use, readable and flexible SSL library"
    settings = "os", "arch", "build_type"
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

    def layout(self):
        cmake_layout(self)

    def source(self):
        folder = self.name
        tag = f"v{self.version}"
        self.output.info(f"Cloning repo: {self.url} dest: {folder} tag: {tag}")
        git = Git(self)
        git.clone(url=self.url, target=folder, args=["--branch", tag])

        patches_dir = os.path.join(self.recipe_folder, "patches")
        if os.path.isdir(patches_dir):
            for patch_file in sorted(os.listdir(patches_dir)):
                patch_path = os.path.join(patches_dir, patch_file)
                self.output.info(f"Applying patch: {patch_path}")
                patch(self, base_path=os.path.join(self.source_folder, folder), patch_file=patch_path)

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["ENABLE_TESTING"] = False
        tc.variables["ENABLE_PROGRAMS"] = False
        if self.settings.os == "Windows":
            tc.variables["MSVC_STATIC_RUNTIME"] = True
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"
        tc.generate()

    def build(self):
        config_h = os.path.join(self.source_folder, self.name, "include", "mbedtls", "mbedtls_config.h")
        mbedtls_configs = ["MBEDTLS_THREADING_C", "MBEDTLS_SSL_PROTO_TLS1_3"]
        if self.settings.os == "Windows":
            mbedtls_configs.append("MBEDTLS_THREADING_WINDOWS")
        else:
            mbedtls_configs.append("MBEDTLS_THREADING_PTHREAD")

        for config in mbedtls_configs:
            config_string = f"#define {config}"
            replace_in_file(self, config_h, f"//{config_string}", config_string, strict=False)

        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()
        cmake.install()

    def package(self):
        copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.h", src=os.path.join(self.source_folder, self.name, "include"), dst=os.path.join(self.package_folder, "include"), keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["mbedtls", "mbedx509", "mbedcrypto", "everest", "p256m"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("bcrypt")
