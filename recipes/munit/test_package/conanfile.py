from conan import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'iOS' or self.settings.os == 'Android':
            return

        if self.settings.os == 'Windows':
            libs = ['munit.lib']
        else:
            libs = ['libmunit.a']
        headers = ['munit.h']

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.dependencies['munit'].package_folder, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.dependencies['munit'].package_folder, 'include', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
