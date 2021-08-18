from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type', 'compiler'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows':
            libs = ['Halide.dll', 'Halide.lib']
        elif self.settings.os == 'Linux':
            libs = ['libHalide.so']
        elif self.settings.os == 'Macos':
            libs = ['libHalide.dylib']
        headers = [
            'Halide.h',
            'HalideBuffer.h',
            'HalideRuntime.h',
            'HalideRuntimeCuda.h',
            'HalideRuntimeD3D12Compute.h',
            'HalideRuntimeHexagonDma.h',
            'HalideRuntimeHexagonHost.h',
            'HalideRuntimeMetal.h',
            'HalideRuntimeOpenCL.h',
            'HalideRuntimeOpenGLCompute.h',
            'HalideRuntimeQurt.h'
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['halide'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['halide'].rootpath, 'include', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
