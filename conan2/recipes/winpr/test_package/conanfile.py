from conan import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["winpr"].package_folder
        libs = ["winpr3.lib"] if self.settings.os == "Windows" else ["libwinpr3.a"]
        headers = [
            "sam.h", "error.h", "strlst.h", "input.h", "winsock.h",
            "debug.h", "shell.h", "pack.h", "tools/makecert.h", "version.h",
            "pool.h", "sspi.h", "synch.h", "timezone.h",
            "nt.h", "library.h", "path.h", "endian.h", "security.h",
            "sysinfo.h", "file.h", "cmdline.h", "winpr.h", "comm.h", "stream.h",
            "sspicli.h", "registry.h", "crypto.h", "windows.h",
            "environment.h", "ini.h", "spec.h", "ntlm.h", "intrin.h",
            "ssl.h", "thread.h", "bitstream.h", "wlog.h", "handle.h", "io.h",
            "user.h", "clipboard.h", "pipe.h", "print.h",
            "wtsapi.h", "crt.h", "interlocked.h", "memory.h", "rpc.h",
            "wtypes.h", "dsparse.h", "schannel.h", "tchar.h", "smartcard.h",
            "platform.h", "image.h", "bcrypt.h", "collections.h",
            "string.h",
        ]

        self.output.info("Testing libraries exist:")
        for lib in libs:
            file_path = os.path.join(package_folder, "lib", lib)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"

        self.output.info("Testing headers exist:")
        for header in headers:
            file_path = os.path.join(package_folder, "include", "winpr", header)
            self.output.info(f"- {file_path}")
            assert os.path.isfile(file_path), f"Missing file: {file_path}"
