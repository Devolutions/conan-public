from conans import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type', 'compiler'

    def build(self):
        pass

    def test(self):
        if self.settings.os == 'Windows':
            libs = ['mbedtls.lib']
        else:
            libs = ['libmbedtls.a', 'libmbedx509.a', 'libmbedcrypto.a']
        headers = [
            'aes.h', 'asn1write.h', 'camellia.h', 'cipher_internal.h', 'debug.h',
            'ecjpake.h', 'error.h', 'md.h', 'memory_buffer_alloc.h', 'pem.h',
            'pkcs5.h', 'rsa.h', 'ssl.h', 'ssl_ticket.h', 'x509_crl.h', 'aesni.h',
            'base64.h', 'ccm.h', 'cmac.h', 'des.h', 'ecp.h', 'gcm.h', 'md2.h',
            'net.h', 'pk.h', 'platform.h', 'rsa_internal.h', 'ssl_cache.h',
            'threading.h', 'x509_crt.h', 'arc4.h', 'bignum.h', 'certs.h',
            'compat-1.3.h', 'dhm.h', 'ecp_internal.h', 'havege.h', 'md4.h',
            'net_sockets.h', 'pk_internal.h', 'platform_time.h', 'sha1.h',
            'ssl_ciphersuites.h', 'timing.h', 'x509_csr.h', 'aria.h', 'blowfish.h',
            'check_config.h', 'config.h', 'ecdh.h', 'entropy.h', 'hkdf.h', 'md5.h',
            'oid.h', 'pkcs11.h', 'platform_util.h', 'sha256.h', 'ssl_cookie.h',
            'version.h', 'xtea.h', 'asn1.h', 'bn_mul.h', 'cipher.h', 'ctr_drbg.h',
            'ecdsa.h', 'entropy_poll.h', 'hmac_drbg.h', 'md_internal.h', 'padlock.h',
            'pkcs12.h', 'ripemd160.h', 'sha512.h', 'ssl_internal.h', 'x509.h'
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.deps_cpp_info['mbedtls'].rootpath, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.deps_cpp_info['mbedtls'].rootpath, 'include', 'mbedtls', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
