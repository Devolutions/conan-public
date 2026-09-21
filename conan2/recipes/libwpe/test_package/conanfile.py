from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["libwpe"].package_folder

        # The soname, not the versioned file: WPE WebKit and WPEBackend-fdo both
        # resolve libwpe through it, and a bundle without it fails at exec time.
        files = [
            os.path.join("lib", "libwpe-1.0.so.1"),
            os.path.join("lib", "pkgconfig", "wpe-1.0.pc"),
            os.path.join("include", "wpe-1.0", "wpe", "wpe.h"),
            os.path.join("include", "wpe-1.0", "wpe", "loader.h"),
        ]

        self.output.info("Testing packaged files exist:")
        for item in files:
            file_path = os.path.join(package_folder, item)
            self.output.info(f"- {file_path}")
            assert os.path.exists(file_path), f"Missing file: {file_path}"
