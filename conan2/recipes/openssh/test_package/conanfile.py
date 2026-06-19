from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["openssh"].package_folder
        binary = "ssh"
        if self.settings.os == "Windows":
            binary += ".exe"

        self.output.info("Testing binary exists:")
        file_path = os.path.join(package_folder, "bin", binary)
        self.output.info(f"- {file_path}")
        assert os.path.isfile(file_path), f"Missing file: {file_path}"
