from conans import ConanFile, CMake, tools, python_requires, VisualStudioBuildEnvironment
import os, glob, shutil

class OpensslConan(ConanFile):
    name = 'openssl'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'OpenSSL'
    url = 'https://github.com/openssl/openssl.git'
    no_copy_source = True
    description = 'TLS/SSL and crypto library'
    settings = 'os', 'arch', 'distro', 'build_type'
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    options = {
        'fPIC': [True, False],
        'shared': [True, False]
    }
    default_options = {
        'fPIC': True,
        'shared': False
    }

    def source(self):
        if self.settings.arch == 'universal':
            return

        openssl_source_dir = os.path.join(self.source_folder, self.name)
        tag = 'OpenSSL_%s' % self.version
        tag = tag.replace('.', '_')

        self.output.info('Cloning repo: %s tag: %s' % (self.url, tag))
        git = tools.Git(folder=openssl_source_dir)
        git.clone(self.url)
        git.checkout(tag)

        openssl_cmake_url = 'https://github.com/devolutions/openssl-cmake.git'
        openssl_cmake_dir = os.path.join(openssl_source_dir, 'openssl-cmake')
        git = tools.Git(folder=openssl_cmake_dir)
        git.clone(openssl_cmake_url)
        git.checkout("cflags-fix")
        git.run("checkout-index -a -f --prefix=../")

        if self.settings.os == 'iOS':
            # patch crypto/err/err_all.c to remove call on ERR_load_DSO_string()
            tools.replace_in_file(os.path.join(openssl_source_dir, 'crypto/err/err_all.c'),
                '        ERR_load_DSO_strings() == 0 ||',
                '# ifndef OPENSSL_NO_DSO\n        ERR_load_DSO_strings() == 0 ||\n# endif')
            # patch crypto/conf/conf_mod.c to remove DSO API calls (disabled anyway)
            tools.replace_in_file(os.path.join(openssl_source_dir, 'crypto/conf/conf_mod.c'),
                '    DSO *dso = NULL;',
                '#if 0\n    DSO *dso = NULL;')
            tools.replace_in_file(os.path.join(openssl_source_dir, 'crypto/conf/conf_mod.c'),
                '    ERR_add_error_data(4, "module=", name, ", path=", path);',
                '    ERR_add_error_data(4, "module=", name, ", path=", path);\n#endif')
            tools.replace_in_file(os.path.join(openssl_source_dir, 'crypto/conf/conf_mod.c'),
                '    DSO_free(md->dso);',
                '    //DSO_free(md->dso);')

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['WITH_APPS'] = 'OFF'
        cmake.definitions['OPENSSL_NO_ENGINE'] = 'ON'
        
        if self.settings.os == 'iOS':
            cmake.definitions['OPENSSL_NO_DSO'] = 'ON'
            cmake.definitions['OPENSSL_NO_ASYNC'] = 'ON'
        
        if self.settings.os == 'iOS':
            cmake.definitions['OPENSSL_RAND_SEED_OS'] = 'OFF'
            cmake.definitions['OPENSSL_RAND_SEED_GETRANDOM'] = 'OFF'
            cmake.definitions['OPENSSL_RAND_SEED_DEVRANDOM'] = 'ON'

        if self.settings.os == 'Windows':
            cmake.definitions['MSVC_RUNTIME'] = 'static'

        openssl_source_dir = os.path.join(self.source_folder, self.name)

        cmake.configure(source_folder=openssl_source_dir)
        cmake.build()

    def package(self):
        if self.settings.arch == 'universal':
            self.copy('*.a', dst='lib', keep_path=False)
            self.copy('*.h', src='include', dst='include')
            return

        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)

        self.copy('*.h', src='openssl/include/openssl', dst='include/openssl', keep_path=False) # CMAKE_SOURCE_DIR
        self.copy('*.h', src='include/openssl', dst='include/openssl', keep_path=False) # CMAKE_BINARY_DIR

    def package_info(self):
        if self.settings.os == 'Windows':
            self.cpp_info.libs = ['libssl', 'libcrypto']
        else:
            self.cpp_info.libs = ['ssl', 'crypto']

        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.OPENSSL_DIR = self.package_folder
