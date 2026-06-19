from conans import ConanFile, tools
import os
import subprocess

class Sysroot(ConanFile):
    name = 'sysroot'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    url = 'https://github.com/Devolutions/CBake.git'
    license = 'MIT'
    description = 'Linux sysroot'
    settings = 'os', 'arch', 'distro'

    def build_requirements(self):
        self.build_requires('cbake/latest@devolutions/stable')

    def build(self):
        cbake_home = self.deps_env_info["cbake"].CBAKE_HOME
        build_script = os.path.join(cbake_home, 'build.ps1')
        self.distro = str(self.settings.distro)
        self.sysroot_arch = { 'x86_64':'amd64', 'armv8':'arm64' }[str(self.settings.arch)]
        self.sysroot_name = "%s-%s" % (self.distro, self.sysroot_arch)
        self.export_dir = os.path.join(self.package_folder, self.sysroot_name)
        os.mkdir(self.package_folder)
        os.mkdir(self.export_dir)

        print("building %s sysroot" % (self.sysroot_name))

        subprocess.run([build_script, "sysroot",
            "-Distribution", self.distro,
            "-Architecture", self.sysroot_arch,
            "-ExportPath", self.export_dir,
            "-SkipPackaging"])

    def package(self):
        self.copy('*', src=self.sysroot_name, dst=self.sysroot_name, keep_path=True)

    def package_info(self):
        self.distro = self.settings.distro
        self.sysroot_arch = { 'x86_64':'amd64', 'armv8':'arm64' }[str(self.settings.arch)]
        self.sysroot_name = "%s-%s" % (self.distro, self.sysroot_arch)
        self.env_info.CMAKE_SYSROOT = os.path.join(self.package_folder, self.sysroot_name)
