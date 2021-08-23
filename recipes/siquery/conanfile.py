from conans import ConanFile, tools, python_requires
import os

class SiqueryConan(ConanFile):
    name = 'siquery'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    url = 'https://github.com/Devolutions/siquery-rs.git'
    license = 'Apache-2.0/MIT'
    description = 'A rust library for system information analytics and monitoring.'
    settings = 'os', 'arch', 'build_type'
    tag = 'v%s' % version
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    def source(self):
        folder = self.name

        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)

    def build(self):
        self.cargo_target = self.rustup_target(self.settings.os, self.settings.arch)

        if self.settings.os == 'Windows':
            os.environ['RUSTFLAGS'] = '-C target-feature=+crt-static'

        with tools.chdir(self.name):
            self.rustup_build(target=self.cargo_target, build_type=self.settings.build_type)

    def package(self):
        exe = self.name
        if self.settings.os == 'Windows':
            exe += '.exe'

        if self.settings.build_type == 'Release':
            if self.settings.os == 'Linux':
                utils.execute('strip -s siquery/target/%s/release/%s' % (self.cargo_target, exe))
            elif self.settings.os == 'Macos':
                utils.execute('strip siquery/target/%s/release/%s' % (self.cargo_target, exe))

        self.copy(exe, src='siquery/target/%s/%s' % (self.cargo_target, str(self.settings.build_type).lower()), dst='bin')
