from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.files import copy
import os

class CBake(ConanFile):
    name = 'cbake'
    exports_sources = "VERSION"
    

    def set_version(self):
        version_path = os.path.join(os.path.dirname(__file__), "VERSION")
        with open(version_path, 'r') as f:
            self.version = f.read().strip()
    url = 'https://github.com/Devolutions/CBake.git'
    license = 'MIT'
    description = 'CBake'
    branch = 'master'
    
    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = Git(self, folder=folder)
        git.clone(url=self.url, target=".")
        git.checkout(commit=self.branch)

    def package(self):
        copy(self, '*', src=os.path.join(self.source_folder, 'cbake'), dst=self.package_folder, keep_path=True)

    def package_info(self):
        self.env_info.CBAKE_HOME = self.package_folder
