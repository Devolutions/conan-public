from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["libvpx"].package_folder
        if self.settings.os == "Windows":
            libs = ["vpx.lib"]
        else:
            libs = ["libvpx.a"]
        headers = [
            "vpx_image.h",
            "vpx_encoder.h",
            "vp8cx.h",
            "vpx_integer.h",
            "vpx_codec.h",
            "vp8.h",
            "vp8dx.h",
            "vpx_decoder.h",
            "vpx_frame_buffer.h",
        ]

        self.output.info("Testing libraries exist:")
        for lib in libs:
            file_path = os.path.join(package_folder, "lib", lib)

            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"

        self.output.info("Testing headers exist:")
        for header in headers:
            file_path = os.path.join(package_folder, "include", "vpx", header)

            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"
