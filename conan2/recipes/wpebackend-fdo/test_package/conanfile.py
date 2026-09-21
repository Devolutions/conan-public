from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["wpebackend-fdo"].package_folder

        files = [
            os.path.join("lib", "libWPEBackend-fdo-1.0.so.1"),
            os.path.join("lib", "pkgconfig", "wpebackend-fdo-1.0.pc"),
        ]

        self.output.info("Testing packaged files exist:")
        for item in files:
            file_path = os.path.join(package_folder, item)
            self.output.info(f"- {file_path}")
            assert os.path.exists(file_path), f"Missing file: {file_path}"
