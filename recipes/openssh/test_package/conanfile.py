from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        binary = 'ssh'
        if self.settings.os == 'Windows':
            binary += '.exe'

        self.output.info('Testing binary exists:')
        file_path = os.path.join(self.deps_cpp_info['openssh'].rootpath, 'bin', binary)

        self.output.info('- %s' % file_path)
        assert os.path.isfile(file_path), 'Missing file: %s' % file_path