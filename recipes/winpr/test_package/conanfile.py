from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows':
            libs = ['winpr3.lib']
        else:
            libs = ['libwinpr3.a']
        headers = [
            'sam.h', 'error.h', 'strlst.h', 'wnd.h', 'input.h', 'winsock.h',
            'debug.h', 'shell.h', 'pack.h', 'tools/makecert.h', 'version.h',
            'pool.h', 'sspi.h', 'synch.h', 'timezone.h',
            'nt.h', 'winhttp.h', 'library.h', 'path.h', 'endian.h', 'security.h',
            'sysinfo.h', 'file.h', 'cmdline.h', 'winpr.h', 'comm.h', 'stream.h',
            'sspicli.h', 'registry.h', 'credui.h', 'crypto.h', 'windows.h',
            'environment.h', 'ini.h', 'spec.h', 'ntlm.h', 'ndr.h', 'intrin.h',
            'ssl.h', 'thread.h', 'bitstream.h', 'wlog.h', 'handle.h', 'io.h',
            'user.h', 'clipboard.h', 'credentials.h', 'pipe.h', 'print.h',
            'wtsapi.h', 'heap.h', 'crt.h', 'interlocked.h', 'memory.h', 'rpc.h',
            'wtypes.h', 'dsparse.h', 'schannel.h', 'tchar.h', 'smartcard.h',
            'platform.h', 'image.h', 'bcrypt.h', 'midl.h', 'collections.h',
            'string.h'
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['winpr'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['winpr'].rootpath, 'include', 'winpr', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
