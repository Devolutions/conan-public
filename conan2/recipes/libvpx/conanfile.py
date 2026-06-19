from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, load, save
from conan.tools.scm import Git
import os


class LibvpxConan(ConanFile):
    name = "libvpx"
    exports = "VERSION", "patches/*"
    license = "WebM"
    url = "https://github.com/webmproject/libvpx.git"
    description = "WebM VP8/VP9 Codec SDK"
    settings = "os", "arch", "build_type"
    no_copy_source = True
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "simd": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "simd": True,
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
        for file in ["CMakeLists.txt", "vpx.pc.in", "vpx_config.h.in", "vpx_version.h.in"]:
            copy(self, file, src=patches_dir, dst=os.path.join(self.source_folder, folder))
        rtcd_path = os.path.join(self.source_folder, folder, "build", "make", "rtcd.pl")
        rtcd = load(self, rtcd_path)
        patched_rtcd = rtcd.replace("  chomp;\r\n  my @pair = split /=/;", "  chomp;\r\n  s/\\r\\z//;\r\n  my @pair = split /=/;")
        patched_rtcd = patched_rtcd.replace("  chomp;\n  my @pair = split /=/;", "  chomp;\n  s/\\r\\z//;\n  my @pair = split /=/;")
        if patched_rtcd == rtcd:
            raise RuntimeError(f"Unable to patch RTCD config parser in {rtcd_path}")
        save(self, rtcd_path, patched_rtcd)

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["CONFIG_MULTITHREAD"] = False
        tc.variables["CONFIG_STATIC_MSVCRT"] = True
        tc.variables["INSTALL_PKG_CONFIG_FILE"] = False
        tc.variables["WITH_SIMD"] = bool(self.options.simd)
        git_perl = "C:/Program Files/Git/usr/bin/perl.exe"
        if self.settings.os == "Windows" and os.path.isfile(git_perl):
            tc.variables["PERL_EXECUTABLE"] = git_perl

        if self.settings.os == "Windows":
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"
            tc.variables["VPX_TARGET_PROCESSOR"] = self._cmake_system_processor()

        if str(self.settings.os) == "Android" and str(self.settings.arch) == "x86":
            tc.variables["WITH_SIMD"] = False

        if str(self.settings.os) == "Windows" and str(self.settings.arch) == "armv8":
            tc.variables["CONFIG_RUNTIME_CPU_DETECT"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()
        cmake.install()

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = ["vpx"]

    def _cmake_system_processor(self):
        arch = str(self.settings.arch)
        if arch == "x86":
            return "x86"
        if arch == "x86_64":
            return "x86_64"
        if arch == "armv8":
            return "arm64"
        return arch
