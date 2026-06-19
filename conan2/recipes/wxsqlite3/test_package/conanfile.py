from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["wxsqlite3"].package_folder
        lib_names = ["sqlite3secure"]

        if self.settings.os == "Windows":
            lib_prefix = ""
            lib_suffix = ".dll"
        elif self.settings.os == "Macos":
            lib_prefix = "lib"
            lib_suffix = ".dylib"
        else:
            lib_prefix = "lib"
            lib_suffix = ".so"

        libs = []
        for lib_name in lib_names:
            libs.append(lib_prefix + lib_name + lib_suffix)

        self.output.info("Testing libraries exist:")
        for lib in libs:
            file_path = os.path.join(package_folder, "lib", lib)

            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"
