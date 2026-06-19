from conan import ConanFile
import glob
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["libcbor"].package_folder
        libs = ["cbor.lib"] if self.settings.os == "Windows" else ["libcbor.a"]

        self.output.info("Testing libraries exist:")
        for lib in libs:
            file_path = os.path.join(package_folder, "lib", lib)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"

        self.output.info("Testing headers exist:")
        include_dir = os.path.join(package_folder, "include", "cbor")
        self.output.info(f"- should have at least 10 headers under {include_dir}")
        headers = glob.glob(os.path.join(include_dir, "*.h"))
        assert len(headers) >= 10, f"Number of headers: {len(headers)}"
