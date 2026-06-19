from conan import ConanFile
from conan.tools.files import copy, download, load
from conan.tools.scm import Git
import bz2
import os
import shutil


class OpenH264Conan(ConanFile):
    name = "openh264"
    exports = "VERSION"
    description = "Pre-built OpenH264 binaries"
    license = "BSD-2-Clause"
    url = "https://github.com/cisco/openh264.git"
    settings = "os", "arch", "build_type"
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    no_copy_source = True

    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()

    def source(self):
        folder = self.name
        tag = f"v{self.version}"
        self.output.info(f"Cloning repo: {self.url} dest: {folder} tag: {tag}")
        git = Git(self)
        git.clone(url=self.url, target=folder, args=["--branch", tag])
        self.output.info(f"Current commit: {Git(self, folder=folder).get_commit()}")

    def build(self):
        filename = self.openh264_filename(self.version)
        extracted_path = os.path.join(self.source_folder, filename)
        bz2_path = f"{extracted_path}.bz2"
        url = f"https://ciscobinary.openh264.org/{filename}.bz2"

        for existing_name in os.listdir(self.source_folder):
            if existing_name.endswith((".dll", ".dylib", ".so", ".bz2")):
                os.remove(os.path.join(self.source_folder, existing_name))

        download(self, url, bz2_path)

        with bz2.BZ2File(bz2_path, "rb") as f_in, open(extracted_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    def package(self):
        copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        headers = os.path.join(self.source_folder, self.name, "codec", "api")
        copy(self, "*.h", src=headers, dst=os.path.join(self.package_folder, "include"), keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["openh264"]
