from conans import ConanFile, tools, CMake, python_requires
import os, shutil

class LibvpxConan(ConanFile):
    name = 'libvpx'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'WebM'
    url = 'https://github.com/webmproject/libvpx.git'
    description = 'WebM VP8/VP9 Codec SDK'
    settings = 'os', 'arch', 'distro', 'build_type'
    no_copy_source = True
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    exports = ['VERSION',
        'patches/CMakeLists.txt',
        'patches/vpx.pc.in',
        'patches/vpx_config.h.in',
        'patches/vpx_version.h.in']

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
        tag = 'v%s' % (self.version)
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(tag)

        patches_dir = os.path.join(self.recipe_folder, "patches")
        for file in ['CMakeLists.txt','vpx.pc.in','vpx_config.h.in','vpx_version.h.in']:
            shutil.copy(os.path.join(patches_dir, file), os.path.join(folder, file))

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        if self.settings.os == "Windows":
            cmake.toolset = 'ClangCL'

        cmake.definitions['BUILD_SHARED_LIBS'] = 'OFF'
        cmake.definitions['CONFIG_MULTITHREAD'] = 'OFF'
        cmake.definitions['CONFIG_STATIC_MSVCRT'] = 'ON'
        cmake.definitions['INSTALL_PKG_CONFIG_FILE'] = 'OFF'

        if self.settings.os == "Windows":
            cmake.definitions['CMAKE_ASM_NASM_COMPILER'] = 'nasm'
        else:
            cmake.definitions['CMAKE_ASM_NASM_COMPILER'] = 'yasm'

        if self.settings.os == 'Android' and self.settings.arch == 'x86':
            cmake.definitions['WITH_SIMD'] = 'OFF'

        if self.settings.os == 'Windows' and self.settings.arch == 'armv8':
            cmake.definitions['CONFIG_RUNTIME_CPU_DETECT'] = 'OFF'

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
