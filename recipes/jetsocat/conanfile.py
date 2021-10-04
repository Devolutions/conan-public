from conans import ConanFile, tools, python_requires
import os

class JetsocatConan(ConanFile):
    name = 'jetsocat'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    url = 'https://github.com/Devolutions/devolutions-gateway.git'
    license = 'Devolutions'
    #tag = 'v%s' % version
    tag = "588d3bc"
    description = 'WebSocket toolkit for Jet protocol related operations.'
    settings = 'os', 'arch', 'distro', 'build_type'
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

        tools.chdir("jetsocat")

        with tools.environment_append(cargo_cbake_env):
            if self.settings.os == 'Windows':
                os.environ['RUSTFLAGS'] = '-C target-feature=+crt-static'

            with tools.chdir(self.name):
                self.cargo_build(target=self.cargo_target, build_type=self.settings.build_type, args='-p jetsocat')

    def package(self):
        self.cargo_target = self.get_cargo_target()
        
        exe_name = self.name
        if self.settings.os == 'Windows':
            exe_name += '.exe'

        build_type = str(self.settings.build_type).lower()
        jetsocat_exe = 'jetsocat/target/%s/%s/%s' % (self.cargo_target, build_type, exe_name)

        if self.settings.build_type == 'Release':
            self.strip_binary(jetsocat_exe)

        self.copy(jetsocat_exe, dst='bin', keep_path=False)
