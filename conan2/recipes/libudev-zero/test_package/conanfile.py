from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        dependency = self.dependencies["libudev-zero"]
        lib_prefix = "" if self.settings.os == "Windows" else "lib"
        lib_suffix = ".lib" if self.settings.os == "Windows" else ".a"

        for lib in [f"{lib_prefix}udev-zero{lib_suffix}"]:
            file_path = os.path.join(dependency.package_folder, "lib", lib)
            self.output.info(f"Testing library exists: {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"

        for header in ["libudev.h"]:
            file_path = os.path.join(dependency.package_folder, "include", header)
            self.output.info(f"Testing header exists: {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"
