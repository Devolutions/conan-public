from conan import ConanFile, tools
import os

class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'build_type'

    def build(self):
        pass

    def test(self):
        lib_names = ['mbedtls', 'mbedx509', 'mbedcrypto', 'everest', 'p256m']
        
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
            'aes.h',
            'aria.h',
            'asn1.h',
            'asn1write.h',
            'base64.h',
            'bignum.h',
            'build_info.h',
            'camellia.h',
            'ccm.h',
            'chacha20.h',
            'chachapoly.h',
            'check_config.h',
            'cipher.h',
            'cmac.h',
            'compat-2.x.h',
            'config_adjust_legacy_crypto.h',
            'config_adjust_legacy_from_psa.h',
            'config_adjust_psa_from_legacy.h',
            'config_adjust_psa_superset_legacy.h',
            'config_adjust_ssl.h',
            'config_adjust_x509.h',
            'config_psa.h',
            'constant_time.h',
            'ctr_drbg.h',
            'debug.h',
            'des.h',
            'dhm.h',
            'ecdh.h',
            'ecdsa.h',
            'ecjpake.h',
            'ecp.h',
            'entropy.h',
            'error.h',
            'gcm.h',
            'hkdf.h',
            'hmac_drbg.h',
            'lms.h',
            'mbedtls_config.h',
            'md.h',
            'md5.h',
            'memory_buffer_alloc.h',
            'net_sockets.h',
            'nist_kw.h',
            'oid.h',
            'pem.h',
            'pk.h',
            'pkcs12.h',
            'pkcs5.h',
            'pkcs7.h',
            'platform_time.h',
            'platform_util.h',
            'platform.h',
            'poly1305.h',
            'private_access.h',
            'psa_util.h',
            'ripemd160.h',
            'rsa.h',
            'sha1.h',
            'sha256.h',
            'sha3.h',
            'sha512.h',
            'ssl_cache.h',
            'ssl_ciphersuites.h',
            'ssl_cookie.h',
            'ssl_ticket.h',
            'ssl.h',
            'threading.h',
            'timing.h',
            'version.h',
            'x509_crl.h',
            'x509_crt.h',
            'x509_csr.h',
            'x509.h'
        ]

        self.output.info('Testing libraries exists:')
        for lib in libs:
            file_path = os.path.join(self.dependencies['mbedtls'].package_folder, 'lib', lib)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(file_path), 'Missing file: %s' % file_path

        self.output.info('Testing headers exists:')
        for header in headers:
            file_path = os.path.join(self.dependencies['mbedtls'].package_folder, 'include', 'mbedtls', header)

            self.output.info('- %s' % file_path)
            assert os.path.isfile(os.path.join(file_path)), 'Missing file: %s' % file_path
