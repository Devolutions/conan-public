from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        dependency = self.dependencies["webview"]
        file_path = os.path.join(dependency.package_folder, "lib", "libWebView.so")
        self.output.info(f"Testing library exists: {file_path}")
        assert os.path.isfile(file_path), f"Missing file: {file_path}"
