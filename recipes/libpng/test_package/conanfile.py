from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type', 'compiler'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows' and self.settings.build_type == 'Release':
            libs = ['libpng16_static.lib']
        elif self.settings.os == 'Windows' and self.settings.build_type == 'Debug':
            libs = ['libpng16_staticd.lib']
        else:
            libs = ['libpng.a']
        headers = [
            'png.h',
            'pnglibconf.h',
            'pngconf.h'
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['libpng'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['libpng'].rootpath, 'include', 'libpng16', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
