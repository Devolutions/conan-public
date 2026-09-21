from conan import ConanFile
import os
import subprocess


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["wpewebkit"].package_folder

        # The helper processes and the injected bundle are as load-bearing as the
        # library: WebKit is multi-process, so a package without them produces an
        # engine that initialises and then aborts on the first page.
        files = [
            os.path.join("lib", "libWPEWebKit-2.0.so.1"),
            os.path.join("lib", "wpe-webkit-2.0", "injected-bundle", "libWPEInjectedBundle.so"),
            os.path.join("libexec", "wpe-webkit-2.0", "WPEWebProcess"),
            os.path.join("libexec", "wpe-webkit-2.0", "WPENetworkProcess"),
        ]

        self.output.info("Testing packaged files exist:")
        for item in files:
            file_path = os.path.join(package_folder, item)
            self.output.info(f"- {file_path}")
            assert os.path.exists(file_path), f"Missing file: {file_path}"

        for helper in ("WPEWebProcess", "WPENetworkProcess"):
            file_path = os.path.join(package_folder, "libexec", "wpe-webkit-2.0", helper)
            assert os.access(file_path, os.X_OK), f"Not executable: {file_path}"

        # The whole reason ENABLE_WPE_LEGACY_API is forced on. Without this symbol the
        # package loads cleanly and then fails when a consumer tries to create a view,
        # which is a far more expensive way to discover the same mistake.
        library = os.path.join(package_folder, "lib", "libWPEWebKit-2.0.so.1")
        symbols = subprocess.run(
            ["nm", "-D", "--defined-only", library],
            capture_output=True, text=True, check=True).stdout
        exported = {line.split()[-1] for line in symbols.splitlines() if line.strip()}

        self.output.info("Testing the legacy WPE backend entry point is exported:")
        assert "webkit_web_view_backend_new" in exported, (
            f"{library} exports no webkit_web_view_backend_new - ENABLE_WPE_LEGACY_API did not take")
