from conans import ConanFile, tools
import os, glob

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows':
            libs = ['libwebm.lib']
        else:
            libs = ['libwebm.a']

        headers = [
            'common/file_util.h',
            'common/hdr_util.h',
            'common/webmids.h',
            'mkvmuxer/mkvmuxer.h',
            'mkvmuxer/mkvmuxertypes.h',
            'mkvmuxer/mkvmuxerutil.h',
            'mkvmuxer/mkvwriter.h',
            'mkvparser/mkvparser.h',
            'mkvparser/mkvreader.h'
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['libwebm'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['libwebm'].rootpath, 'include', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path
