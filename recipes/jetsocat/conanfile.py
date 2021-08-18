from conans import ConanFile, tools, python_requires
import os

utils = python_requires('utils/latest@devolutions/stable')

class JetsocatConan(ConanFile):
    name = 'jetsocat'
    exports = 'VERSION', 'REVISION'
    upstream_version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    revision = open(os.path.join('.', 'REVISION'), 'r').read().rstrip()
    version = '%s-%s' % (upstream_version, revision)
    url = 'https://github.com/Devolutions/devolutions-gateway.git'
    license = 'Devolutions'
    description = 'WebSocket toolkit for Jet protocol related operations.'
    settings = 'os', 'arch', 'build_type', 'compiler'

    def build(self):
        arch = self.settings.arch
        if self.settings.os == "Macos":
            if self.settings.arch == "armv8":
                arch = "arm64"

        file = "jetsocat_%s_%s_%s" % (self.settings.os, self.upstream_version, arch)
        if self.settings.os == 'Windows':
            file += '.exe'
        url = "https://github.com/Devolutions/devolutions-gateway/releases/download/v%s/%s" % (self.upstream_version, file)
        filename = self.name
        if self.settings.os == 'Windows':
            filename += '.exe'  
        tools.download(url, filename)

    def package(self):
        filename = self.name
        if self.settings.os == 'Windows':
            filename += '.exe'  
        self.copy(filename, dst='bin')
