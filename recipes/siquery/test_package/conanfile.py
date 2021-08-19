from conans import ConanFile, tools, python_requires
import os, shutil

utils = python_requires('utils/latest@devolutions/stable')

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        # testing real package
        binary = 'siquery'
        if self.settings.os == 'Windows':
            binary += '.exe'

        self.output.info('Testing binary exists:')
        file_path = os.path.join(self.deps_cpp_info['siquery'].rootpath, 'bin', binary)

        self.output.info('- %s' % file_path)
        assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        # testing exported artifacts that will be uploaded to artifactory
        self.output.info('Testing exported artifacts:')
        artifacts_dir = os.path.join(self.deps_cpp_info['siquery'].rootpath, '..', '..', 'artifacts')
        artifacts_dir = os.path.join(artifacts_dir, str(self.settings.os), str(self.settings.arch))
        artifacts_dir = os.path.abspath(artifacts_dir)

        if not os.path.isdir(artifacts_dir):
            self.output.warn('No archive directory, skipping tests')
            return True

        files_to_test = [
            binary
        ]

        for file in files_to_test:
            file_path = os.path.join(artifacts_dir, file)
            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path)

