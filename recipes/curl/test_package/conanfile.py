from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows' and self.settings.build_type == 'Release':
            libs = ['libcurl.lib']
        elif self.settings.os == 'Windows' and self.settings.build_type == 'Debug':
            libs = ['libcurl-d.lib']
        elif self.settings.build_type == 'Release':
            libs = ['libcurl.a']
        elif self.settings.build_type == 'Debug':
            libs = ['libcurl-d.a']
        headers = [
            'stdcheaders.h', 'mprintf.h', 'easy.h', 'curl.h', 'curlver.h',
            'system.h', 'typecheck-gcc.h', 'multi.h'
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['curl'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['curl'].rootpath, 'include', 'curl', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
