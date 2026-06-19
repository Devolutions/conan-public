from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, load, replace_in_file
from conan.tools.scm import Git
import os


class LibcborConan(ConanFile):
    name = "libcbor"
    exports = "VERSION"
    license = "MIT"
    url = "https://github.com/pjk/libcbor"
    description = "libcbor"
    settings = "os", "arch", "build_type"
    no_copy_source = True
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
        branch = f"v{self.version}"
        self.output.info(f"Cloning repo: {self.url} dest: {folder} branch: {branch}")
        git = Git(self)
        git.clone(url=self.url, target=folder, args=["--branch", branch])

        cmake_lists = os.path.join(self.source_folder, folder, "CMakeLists.txt")
        replace_in_file(self, cmake_lists, "cmake_minimum_required(VERSION 3.0)", "cmake_minimum_required(VERSION 3.15)")
        replace_in_file(self, cmake_lists, "set(use_lto FALSE)", "set(use_lto TRUE)")
        replace_in_file(self, cmake_lists, "    check_ipo_supported(RESULT use_lto)", "    #check_ipo_supported(RESULT use_lto)")

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["SANITIZE"] = False
        tc.variables["WITH_TESTS"] = False
        tc.variables["WITH_EXAMPLES"] = False
        if self.settings.os == "Windows":
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
