from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type', 'compiler'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows':
            libs = ['vpx.lib']
        else:
            libs = ['libvpx.a']
        headers = [
            'vpx_image.h',
            'vpx_encoder.h',
            'vp8cx.h',
            'vpx_integer.h',
            'vpx_codec.h',
            'vp8.h',
            'vp8dx.h',
            'vpx_decoder.h',
            'vpx_frame_buffer.h',
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['libvpx'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['libvpx'].rootpath, 'include', 'vpx', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
