from conans import ConanFile, tools
import os
import re
import subprocess


class Sysroot(ConanFile):
    name = 'sysroot'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    url = 'https://github.com/Devolutions/CBake.git'
    license = 'MIT'
    description = 'Linux sysroot'
    settings = 'os', 'arch', 'distro'
    options = {
        'source': ['prebuilt', 'build'],
        'release': 'ANY',
    }
    default_options = {
        'source': 'prebuilt',
        'release': 'v2026.01.15.0',
    }

    def build_requirements(self):
        if self.options.source == 'build':
            self.build_requires('cbake/latest@devolutions/stable')

    def build(self):
        sysroot_dir = os.path.join(self.build_folder, self._sysroot_name())
        tools.rmdir(sysroot_dir)
        if self.options.source == 'prebuilt':
            self._download_prebuilt_sysroot()
        else:
            self._build_sysroot()
        self._validate_sysroot(sysroot_dir)

    def package(self):
        sysroot_name = self._sysroot_name()
        sysroot_dir = os.path.join(self.build_folder, sysroot_name)
        self._validate_sysroot(sysroot_dir)
        self.copy('*', src=sysroot_dir, dst=sysroot_name, keep_path=True, symlinks=True)
        self._validate_sysroot(os.path.join(self.package_folder, sysroot_name))

    def package_info(self):
        self.env_info.CMAKE_SYSROOT = os.path.join(self.package_folder, self._sysroot_name())

    def _download_prebuilt_sysroot(self):
        filename = '%s-sysroot.tar.xz' % self._sysroot_name()
        release_url = 'https://github.com/Devolutions/CBake/releases/download/%s' % self.options.release
        checksums_path = os.path.join(self.build_folder, 'checksums')
        tools.download('%s/checksums' % release_url, checksums_path, overwrite=True)
        sha256 = self._checksum_for(checksums_path, filename)
        tools.get('%s/%s' % (release_url, filename), destination=self.build_folder,
                  sha256=sha256, strip_root=False, overwrite=True)

    def _build_sysroot(self):
        cbake_home = self.deps_env_info["cbake"].CBAKE_HOME
        build_script = os.path.join(cbake_home, 'build.ps1')
        export_dir = os.path.join(self.build_folder, self._sysroot_name())
        tools.mkdir(export_dir)
        subprocess.run(['pwsh', '-File', build_script, 'sysroot',
                        '-Distribution', str(self.settings.distro),
                        '-Architecture', self._sysroot_arch(),
                        '-ExportPath', export_dir,
                        '-SkipPackaging'], check=True)

    @staticmethod
    def _checksum_for(checksums_path, filename):
        with open(checksums_path, 'r', encoding='utf-8') as checksums:
            for line in checksums:
                parts = line.strip().split()
                if len(parts) == 2 and parts[1].lstrip('*') == filename:
                    if not re.fullmatch(r'[0-9a-fA-F]{64}', parts[0]):
                        raise RuntimeError('Invalid SHA256 checksum for %s' % filename)
                    return parts[0].lower()
        raise RuntimeError('No checksum found for %s in %s' % (filename, checksums_path))

    def _sysroot_name(self):
        return '%s-%s' % (self.settings.distro, self._sysroot_arch())

    def _sysroot_arch(self):
        return {'x86_64': 'amd64', 'armv8': 'arm64'}[str(self.settings.arch)]

    @staticmethod
    def _validate_sysroot(path):
        usr_dir = os.path.join(path, 'usr')
        if not os.path.isdir(usr_dir):
            raise RuntimeError('Sysroot was not generated correctly; missing expected directory: %s' % usr_dir)
