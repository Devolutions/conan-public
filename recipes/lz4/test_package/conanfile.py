from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type', 'compiler'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows':
            libs = ['lz4.lib']
        else:
            libs = ['liblz4.a']
        headers = ['lz4.h', 'lz4frame.h', 'lz4hc.h']

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['lz4'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['lz4'].rootpath, 'include', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
