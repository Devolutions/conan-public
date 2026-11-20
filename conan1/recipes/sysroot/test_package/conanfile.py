from conans import ConanFile
import os


class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'distro'

    def build(self):
        pass

    def test(self):
        arch = {'x86_64': 'amd64', 'armv8': 'arm64'}[str(self.settings.arch)]
        name = '%s-%s' % (self.settings.distro, arch)
        expected = os.path.join(self.deps_cpp_info['sysroot'].rootpath, name)
        actual = self.deps_env_info['sysroot'].CMAKE_SYSROOT
        if actual != expected:
            raise RuntimeError('Unexpected CMAKE_SYSROOT: %s (expected %s)' % (actual, expected))
        if not os.path.isfile(os.path.join(actual, 'usr', 'include', 'stdio.h')):
            raise RuntimeError('Missing sysroot C header in %s' % actual)
