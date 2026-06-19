from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["libpng"].package_folder
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            libs = ["libpng16_staticd.lib"]
        elif self.settings.os == "Windows":
            libs = ["libpng16_static.lib"]
        else:
            libs = ["libpng.a"]
        headers = ["png.h", "pnglibconf.h", "pngconf.h"]

        self.output.info("Testing libraries exist:")
        for lib in libs:
            file_path = os.path.join(package_folder, "lib", lib)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"

        self.output.info("Testing headers exist:")
        for header in headers:
            file_path = os.path.join(package_folder, "include", "libpng16", header)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"
