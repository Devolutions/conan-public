from conan import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows':
            binaries = ['yarc.exe']
        else:
            binaries = ['yarc']

        self.output.info('Testing binaries exists:')
        for bin in binaries:
            file_path = os.path.join(self.dependencies['yarc'].package_folder, 'bin', bin)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path
