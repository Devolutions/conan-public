from conans import ConanFile, tools, python_requires
import os

rustup = python_requires('rustup/0.4.4@devolutions/stable')
utils = python_requires('utils/latest@devolutions/stable')

class SiqueryConan(ConanFile):
    name = 'siquery'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    url = 'https://github.com/Devolutions/siquery-rs.git'
    license = 'Devolutions'
    description = 'A rust library for system information analytics and monitoring.'
    settings = 'os', 'arch', 'build_type', 'compiler'
    tag = 'v%s' % upstream_version

    def build_requirements(self):
        self.cargo_target = rustup.target(self.settings.os, self.settings.arch)

    def source(self):
        folder = self.name

        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)

    def build(self):
        if self.settings.os == 'Windows':
            os.environ['RUSTFLAGS'] = '-C target-feature=+crt-static'

        with tools.chdir(self.name):
            rustup.build(target=self.cargo_target, build_type=self.settings.build_type)

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
