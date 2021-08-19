from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows':
            libs = ['nng.lib']
        else:
            libs = ['libnng.a']
        headers = [
            'compat/nanomsg/tcp.h', 'compat/nanomsg/bus.h', 'compat/nanomsg/reqrep.h',
            'compat/nanomsg/ipc.h', 'compat/nanomsg/ws.h', 'compat/nanomsg/pubsub.h',
            'compat/nanomsg/inproc.h', 'compat/nanomsg/nn.h', 'compat/nanomsg/survey.h',
            'compat/nanomsg/pair.h', 'compat/nanomsg/pipeline.h', 
            'protocol/pair1/pair.h', 'protocol/reqrep0/req.h', 'protocol/reqrep0/rep.h',
            'protocol/pair0/pair.h', 'protocol/pubsub0/pub.h', 'protocol/pubsub0/sub.h',
            'protocol/pipeline0/pull.h', 'protocol/pipeline0/push.h', 'protocol/survey0/respond.h',
            'protocol/survey0/survey.h', 'protocol/bus0/bus.h', 
            'supplemental/util/options.h', 'supplemental/util/platform.h', 'supplemental/tls/tls.h',
            'supplemental/http/http.h',
            'transport/inproc/inproc.h',
            'transport/tls/tls.h', 'transport/tcp/tcp.h', 'transport/ipc/ipc.h',
            'transport/zerotier/zerotier.h', 'transport/ws/websocket.h', 
            'nng.h'
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['nng'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['nng'].rootpath, 'include', 'nng', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
