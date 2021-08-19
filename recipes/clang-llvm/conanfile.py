from conans import ConanFile, tools, CMake, python_requires

import glob
import os
import shutil

class ClangLlvmConan(ConanFile):
    name = 'clang-llvm'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'Apache 2.0'
    url = 'https://github.com/llvm/llvm-project.git'
    description = 'LLVM Compiler'
    settings = 'os_build', 'arch_build'
    no_copy_source = True
    short_paths = True

    def source(self):
        self.pkg_version = self.version
        self.pkg_platform = {'Windows':'windows', 'Macos':'macos', 'Linux':'linux'}[str(self.settings.os_build)]
        self.pkg_arch = "x86_64"
        self.pkg_ext = ".tar.xz"
        self.dir_name = "clang+llvm-%s-%s-%s" % (self.pkg_version, self.pkg_arch, self.pkg_platform)
        archive_name = "%s%s" % (self.dir_name, self.pkg_ext)
        base_url = "https://github.com/awakecoding/llvm-prebuilt/releases/download"
        download_url = "%s/v%s/clang+llvm-%s-%s-%s%s" % (base_url,
            self.pkg_version, self.pkg_version, self.pkg_arch, self.pkg_platform, self.pkg_ext)
        tools.download(download_url, archive_name)

    def build(self):
        archive_name = "%s%s" % (self.dir_name, self.pkg_ext)
        archive_path = os.path.join(self.source_folder, archive_name)
        tools.untargz(archive_path)
        shutil.move(self.dir_name, "llvm")

    def package(self):
        self.copy('*', src='llvm', dst='', symlinks=True, keep_path=True)
