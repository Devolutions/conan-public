from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["freerdp"].package_folder
        lib_names = ["freerdp3", "freerdp-client3"]

        if self.settings.os == "Windows":
            lib_prefix = ""
            lib_suffix = ".lib"
        else:
            lib_prefix = "lib"
            lib_suffix = ".a"

        libs = [f"{lib_prefix}{lib_name}{lib_suffix}" for lib_name in lib_names]
        headers = [
            "api.h",
            "error.h",
            "client.h",
            "freerdp.h",
            "settings.h",
            "version.h",
            "channels/channels.h",
            "client/channels.h",
            "codec/color.h",
            "crypto/crypto.h",
            "gdi/gdi.h",
            "locale/keyboard.h",
            "utils/pcap.h",
        ]

        self.output.info("Testing libraries exist:")
        for lib in libs:
            file_path = os.path.join(package_folder, "lib", lib)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"

        self.output.info("Testing headers exist:")
        for header in headers:
            file_path = os.path.join(package_folder, "include", "freerdp", header)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"
