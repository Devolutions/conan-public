from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type', 'compiler'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows':
            libs = ['xpp.lib']
        else:
            libs = ['libxpp.a']
        headers = ['primitive.h', 'scale.h', 'color.h', 'xpp.h', 'compare.h', 'simd.h', 'math.h', 'platform.h', 'copy.h']

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['xpp'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['xpp'].rootpath, 'include', 'xpp', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
