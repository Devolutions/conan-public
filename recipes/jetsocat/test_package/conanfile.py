from conans import ConanFile, tools, python_requires
import os, shutil

utils = python_requires('utils/latest@devolutions/stable')

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type', 'compiler'

    def build(self):
        pass

    def test(self):
        # testing real package
        binary = 'jetsocat'
        if self.settings.os == 'Windows':
            binary += '.exe'

        self.output.info('Testing binary exists:')
        file_path = os.path.join(self.deps_cpp_info['jetsocat'].rootpath, 'bin', binary)

        self.output.info('- %s' % file_path)
        assert os.path.isfile(file_path), 'Missing file: %s' % file_path
