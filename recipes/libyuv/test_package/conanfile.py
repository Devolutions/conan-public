from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows':
            libs = ['libyuv.lib']
        else:
            libs = ['libyuv.a']
        headers = [
            'basic_types.h',
            'compare.h',
            'compare_row.h',
            'convert.h',
            'convert_argb.h',
            'convert_from.h',
            'convert_from_argb.h',
            'cpu_id.h',
            'libyuv.h',
            'macros_msa.h',
            'mjpeg_decoder.h',
            'planar_functions.h',
            'rotate.h',
            'rotate_argb.h',
            'rotate_row.h',
            'row.h',
            'scale.h',
            'scale_argb.h',
            'scale_row.h',
            'version.h',
            'video_common.h'
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['libyuv'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['libyuv'].rootpath, 'include', 'libyuv', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
