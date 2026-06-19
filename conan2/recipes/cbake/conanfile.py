from conan import ConanFile
from conan.tools.files import copy, load
from conan.tools.scm import Git
import os


class CBake(ConanFile):
    name = "cbake"
    exports = "VERSION"
    url = "https://github.com/Devolutions/CBake.git"
    license = "MIT"
    description = "CBake"
    branch = "master"
    no_copy_source = True

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()

    def source(self):
        folder = self.name
        self.output.info(f"Cloning repo: {self.url} dest: {folder} branch: {self.branch}")
        git = Git(self)
        git.clone(url=self.url, target=folder, args=["--branch", self.branch])

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder, "cbake"), dst=self.package_folder, excludes=(".git", ".git/*"))

    def package_info(self):
        self.buildenv_info.define_path("CBAKE_HOME", self.package_folder)
        self.runenv_info.define_path("CBAKE_HOME", self.package_folder)
