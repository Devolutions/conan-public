from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, load, patch
from conan.tools.scm import Git
import os
import shutil


class LibUdevZeroConan(ConanFile):
    name = "libudev-zero"
    exports = "VERSION", "patches/*"
    license = "ISC"
    url = "https://github.com/illiliti/libudev-zero"
    description = "libudev-zero"
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
        tag = self.version
        self.output.info(f"Cloning repo: {self.url} dest: {folder} tag: {tag}")
        git = Git(self)
        git.clone(url=self.url, target=folder)
        Git(self, folder=folder).checkout(commit=tag)

        patches_dir = os.path.join(self.recipe_folder, "patches")
        shutil.copy(os.path.join(patches_dir, "CMakeLists.txt"), os.path.join(self.source_folder, folder, "CMakeLists.txt"))

        for patch_file in sorted(os.listdir(patches_dir)):
            if patch_file.endswith(".patch"):
                patch_path = os.path.join(patches_dir, patch_file)
                self.output.info(f"Applying patch: {patch_path}")
                patch(self, base_path=os.path.join(self.source_folder, folder), patch_file=patch_path)

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()
        cmake.install()

    def package(self):
        return

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
