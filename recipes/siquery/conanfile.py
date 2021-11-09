from conans import ConanFile, tools, python_requires
import os

class SiqueryConan(ConanFile):
    name = 'siquery'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    url = 'https://github.com/Devolutions/siquery-rs.git'
    license = 'Apache-2.0/MIT'
    description = 'A rust library for system information analytics and monitoring.'
    settings = 'os', 'arch', 'distro', 'build_type'
    #tag = 'v%s' % version
    tag = '89f59bb'
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.tag)

    def build(self):
        self.cargo_target = self.get_cargo_target()
        cargo_cbake_env = self.get_cargo_cbake_env()

        with tools.environment_append(cargo_cbake_env):
            if self.settings.os == 'Windows':
                os.environ['RUSTFLAGS'] = '-C target-feature=+crt-static'

            with tools.chdir(self.name):
                self.cargo_build(target=self.cargo_target, build_type=self.settings.build_type)

    def package(self):
        utils = self.python_requires["shared"].module
        self.cargo_target = self.get_cargo_target()
        
        exe_name = self.name
        if self.settings.os == 'Windows':
            exe_name += '.exe'

        build_type = str(self.settings.build_type).lower()
        siquery_exe = 'siquery/target/%s/%s/%s' % (self.cargo_target, build_type, exe_name)

        if self.settings.build_type == 'Release':
            self.strip_binary(siquery_exe)

        self.copy(siquery_exe, dst='bin', keep_path=False)
