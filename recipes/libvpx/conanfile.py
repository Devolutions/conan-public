from conans import ConanFile, tools, CMake, python_requires
import os

class LibvpxConan(ConanFile):
    name = 'libvpx'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'WebM'
    url = 'https://github.com/awakecoding/libvpx.git'
    description = 'WebM VP8/VP9 Codec SDK'
    settings = 'os', 'arch', 'build_type'
    no_copy_source = True
    short_paths = True
    branch = 'cmake'
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

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['BUILD_SHARED_LIBS'] = 'OFF'
        cmake.definitions['CONFIG_MULTITHREAD'] = 'OFF'
        cmake.definitions['CONFIG_STATIC_MSVCRT'] = 'ON'
        cmake.definitions['INSTALL_PKG_CONFIG_FILE'] = 'OFF'

        if self.settings.os == 'Android' and self.settings.arch == 'x86':
            cmake.definitions['WITH_SIMD'] = 'OFF'

        cmake.configure(source_folder=self.name)
        
        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.arch == 'universal':
            self.copy('*.a', dst='lib', keep_path=False)
            self.copy('*.h', src='include', dst='include')
            return

    def package_info(self):
        self.cpp_info.libs = ['vpx']
