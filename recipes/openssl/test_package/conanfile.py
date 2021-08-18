from conans import ConanFile, tools
import os, glob

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type', 'compiler'

    def build(self):
        pass

    def test(self):

        lib_names = ['crypto', 'ssl']

        if self.settings.os == 'Windows':
            lib_prefix = 'lib'
            lib_suffix = '.lib'
        else:
            lib_prefix = 'lib'
            lib_suffix = '.a'

        libs = []
        for lib_name in lib_names:
            libs.append(lib_prefix + lib_name + lib_suffix)

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['openssl'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        self.output.warn('We are only checking if there is the right number of headers')

        include_dir = os.path.join(self.deps_cpp_info['openssl'].rootpath, 'include', 'openssl')
        self.output.info('- should have at least 104 headers under %s' % include_dir)
        headers = glob.glob('%s/*.h' % include_dir)
        assert len(headers) >= 104, 'Number of headers: %s' % len(headers)
