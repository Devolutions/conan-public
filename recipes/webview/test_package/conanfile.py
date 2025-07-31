from conan import ConanFile, tools
import os, glob

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        libs = ['libWebView.so']

        self.output.info('Testing libraries exist:')
        
        for lib in libs:
            file_path = os.path.join(self.dependencies['webview'].package_folder, 'lib', lib)
            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path
