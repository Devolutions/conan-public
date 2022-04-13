from conans import ConanFile, tools, CMake, python_requires
import os

class LibreSSLConan(ConanFile):
    name = 'libressl'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'BSD'
    url = 'https://github.com/awakecoding/LibreSSL.git'
    description = 'LibreSSL'
    settings = 'os', 'arch', 'distro', 'build_type'
    no_copy_source = False
    branch = 'devolutions'
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

    def build_requirements(self):
        super().build_requirements()

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.branch)

        if self.settings.os == 'iOS':
            tools.replace_in_file(os.path.join(folder, 'CMakeLists.txt'),
                "check_function_exists(syslog_r HAVE_SYSLOG_R)",
                "#check_function_exists(syslog_r HAVE_SYSLOG_R)")

            tools.replace_in_file(os.path.join(folder, 'CMakeLists.txt'),
                "check_function_exists(syslog HAVE_SYSLOG)",
                "#check_function_exists(syslog HAVE_SYSLOG)")

            tools.replace_in_file(os.path.join(folder, 'CMakeLists.txt'),
                "check_function_exists(explicit_bzero HAVE_EXPLICIT_BZERO)",
                "#check_function_exists(explicit_bzero HAVE_EXPLICIT_BZERO)")

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        cmake.definitions['CMAKE_INSTALL_LIBEXECDIR'] = "lib"
        cmake.definitions['BUILD_SHARED_LIBS'] = 'ON' if self.options.shared else 'OFF'

        if self.settings.os == 'iOS' or self.settings.os == 'Android':
            cmake.definitions['LIBRESSL_APPS'] = 'OFF'
        else:
            cmake.definitions['LIBRESSL_APPS'] = 'ON'
            
        cmake.definitions['LIBRESSL_TESTS'] = 'OFF'

        cmake.configure(source_folder=self.name)
        
        cmake.build()
        cmake.install()

    def package(self):
        return

    def package_info(self):
        if self.settings.os == 'Windows':
            self.cpp_info.libs = ['libssl', 'libcrypto', 'libtls']
        else:
            self.cpp_info.libs = ['ssl', 'crypto', 'tls']

        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.OPENSSL_DIR = self.package_folder
