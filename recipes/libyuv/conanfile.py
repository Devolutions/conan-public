from conans import ConanFile, CMake, tools, python_requires
import os

class LibyuvConan(ConanFile):
    name = 'libyuv'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'BSD'
    no_copy_source = True
    url = 'https://github.com/Devolutions/libyuv.git'
    description = 'YUV scaling and conversion functionality'
    settings = 'os', 'arch', 'distro', 'build_type'
    tag = '639dd4e'
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

        folder = self.name
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
        git = tools.Git(folder)
        git.clone(self.url)
        git.checkout(self.tag)

        os.chdir(folder)
        tools.replace_in_file("CMakeLists.txt",
            "CMAKE_MINIMUM_REQUIRED( VERSION 2.8 )", "CMAKE_MINIMUM_REQUIRED( VERSION 3.0 )")
        tools.replace_in_file("CMakeLists.txt",
            "ADD_EXECUTABLE			( yuvconvert", "#ADD_EXECUTABLE			( yuvconvert")
        tools.replace_in_file("CMakeLists.txt",
            "TARGET_LINK_LIBRARIES	( yuvconvert", "#TARGET_LINK_LIBRARIES	( yuvconvert")
        tools.replace_in_file("CMakeLists.txt",
            "if (JPEG_FOUND)", "if (JPEG_FALSE)")
        tools.replace_in_file("CMakeLists.txt",
            "INCLUDE ( CM_linux_packages.cmake )", "")

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['BUILD_SHARED_LIBS'] = 'OFF'
        cmake.definitions['CMAKE_STATIC_LIBRARY_PREFIX_CXX'] = 'lib'

        if self.settings.os == 'Android':
            cmake.definitions['ANDROID_TOOLCHAIN'] = 'clang'

        cmake.configure(source_folder=self.name)
        
        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        elif self.settings.arch == 'universal':
            self.copy('*.a', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib')

        self.copy('*.h', src='libyuv/include', dst='include/libyuv', keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
