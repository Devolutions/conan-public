from conan import ConanFile, tools
import os, glob

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):

        lib_names = ['pcre2-8', 'pcre2-16', 'pcre2-32']

        if self.settings.os == 'Windows':
            lib_prefix = ''
            lib_suffix = '.lib'
        else:
            lib_prefix = 'lib'
            lib_suffix = '.a'

        libs = []
        for lib_name in lib_names:
            if self.settings.os == "Windows" and self.settings.build_type == "Debug":
               lib_name += 'd'
            libs.append(lib_prefix + lib_name + lib_suffix)

        headers = [
            'pcre2.h',
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.dependencies['pcre2'].package_folder, 'lib', lib)
            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.dependencies['pcre2'].package_folder, 'include', header)
            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
