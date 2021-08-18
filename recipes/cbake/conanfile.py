from conans import ConanFile, tools
import os

class CBake(ConanFile):
    name = 'cbake'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    license = 'Devolutions'
    url = 'https://github.com/Devolutions/CBake.git'
    description = 'CBake'
    branch = 'master'

    def source(self):
        folder = self.name

        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.branch)

    def package(self):
        self.copy('*.cmake', keep_path=False)

