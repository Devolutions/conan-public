from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["libjpeg"].package_folder
        libs = ["jpeg-static.lib", "turbojpeg-static.lib"] if self.settings.os == "Windows" else ["libjpeg.a", "libturbojpeg.a"]
        headers = ["jpeglib.h", "jerror.h", "turbojpeg.h", "jconfig.h", "jmorecfg.h"]

        self.output.info("Testing libraries exist:")
        for lib in libs:
            file_path = os.path.join(package_folder, "lib", lib)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"

        self.output.info("Testing headers exist:")
        for header in headers:
            file_path = os.path.join(package_folder, "include", header)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"
