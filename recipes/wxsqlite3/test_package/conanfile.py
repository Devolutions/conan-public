from conan import ConanFile, tools
import os, glob

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        lib_names = ['sqlite3secure']

        if self.settings.os == 'Windows':
            lib_prefix = ''
            lib_suffix = '.dll'
        elif self.settings.os == 'Macos':
            lib_prefix = 'lib'
            lib_suffix = '.dylib'
        else:
            lib_prefix = 'lib'
            lib_suffix = '.so'

        libs = []
        for lib_name in lib_names:
            libs.append(lib_prefix + lib_name + lib_suffix)

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.dependencies['wxsqlite3'].package_folder, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path
