from conans import ConanFile, tools
import os, glob

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        lib_names = ['udev-zero']

        if self.settings.os == 'Windows':
            lib_prefix = ''
            lib_suffix = '.lib'
        else:
            lib_prefix = 'lib'
            lib_suffix = '.a'

        libs = []
        for lib_name in lib_names:
            libs.append(lib_prefix + lib_name + lib_suffix)

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['libudev-zero'].rootpath, 'lib', lib)
            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        hdrs = ['libudev.h']
        self.output.info('Testing headers exists:')
        for hdr in hdrs:
            file_path = os.path.join(self.deps_cpp_info['libudev-zero'].rootpath, 'include', hdr)
            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path
