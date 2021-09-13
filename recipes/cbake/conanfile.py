from conans import ConanFile, tools
import os

class CBake(ConanFile):
    name = 'cbake'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    url = 'https://github.com/Devolutions/CBake.git'
    license = 'MIT'
    description = 'CBake'
    branch = 'sysroot-fixes'
    
    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.branch)

    def package(self):
        self.copy('*', src='cbake', dst='', keep_path=True)

    def package_info(self):
        self.env_info.CBAKE_HOME = self.package_folder
