from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, load, replace_in_file
from conan.tools.scm import Git
import os


class ZlibConan(ConanFile):
    name = "zlib"
    exports = "VERSION"
    license = "Zlib"
    url = "https://github.com/madler/zlib.git"
    description = "zlib is a general purpose data compression library."
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

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        if self.settings.os == "Windows":
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"
        tc.generate()

    def build(self):
        if self.settings.os == "Windows":
            replace_in_file(
                self,
                os.path.join(self.source_folder, self.name, "CMakeLists.txt"),
                'set(CMAKE_DEBUG_POSTFIX "d")',
                'set(CMAKE_DEBUG_POSTFIX "")',
                strict=False,
            )

        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()

    def package(self):
        if self.settings.os == "Windows":
            lib_dir = os.path.join(self.package_folder, "lib")
            copy(self, "*.lib", src=self.build_folder, dst=lib_dir, keep_path=False)

            zlibstatic = os.path.join(lib_dir, "zlibstatic.lib")
            zlib = os.path.join(lib_dir, "zlib.lib")
            if not os.path.isfile(zlibstatic):
                raise RuntimeError(f"Missing expected static library: {zlibstatic}")
            if os.path.isfile(zlib):
                os.remove(zlib)
            os.replace(zlibstatic, zlib)
        else:
            copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

        copy(self, "zconf.h", src=self.build_folder, dst=os.path.join(self.package_folder, "include"), keep_path=False)
        copy(self, "zlib.h", src=os.path.join(self.source_folder, self.name), dst=os.path.join(self.package_folder, "include"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["zlib"] if self.settings.os == "Windows" else ["z"]
