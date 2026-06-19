from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["mbedtls"].package_folder
        libs = ["mbedtls", "mbedx509", "mbedcrypto", "everest", "p256m"]
        libs = [f"{lib}.lib" for lib in libs] if self.settings.os == "Windows" else [f"lib{lib}.a" for lib in libs]
        headers = ["aes.h", "ssl.h", "threading.h", "version.h", "x509.h", "mbedtls_config.h"]

        self.output.info("Testing libraries exist:")
        for lib in libs:
            file_path = os.path.join(package_folder, "lib", lib)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"

        self.output.info("Testing representative headers exist:")
        for header in headers:
            file_path = os.path.join(package_folder, "include", "mbedtls", header)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"
