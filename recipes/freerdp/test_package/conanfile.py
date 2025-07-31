from conan import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        lib_names = [
            'freerdp3',
            'freerdp-client3'
        ]
        
        if self.settings.os == 'Windows':
            lib_prefix = ''
            lib_suffix = '.lib'
        else:
            lib_prefix = 'lib'
            lib_suffix = '.a'

        libs = []
        for lib_name in lib_names:
            libs.append(lib_prefix + lib_name + lib_suffix)

        headers = [
            'api.h',
            'error.h',
            'client.h',
            'freerdp.h',
            'settings.h',
            'version.h',
            'channels/channels.h',
            'client/channels.h',
            'codec/color.h',
            'crypto/crypto.h',
            'gdi/gdi.h',
            'locale/keyboard.h',
            'utils/pcap.h'
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.dependencies['freerdp'].package_folder, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.dependencies['freerdp'].package_folder, 'include', 'freerdp', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
