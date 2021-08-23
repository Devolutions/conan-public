from conans import ConanFile, tools, CMake, python_requires
import os

class LibwebmConan(ConanFile):
    name = 'libwebm'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'WebM'
    url = 'https://github.com/webmproject/libwebm.git'
    description = 'WebM'
    settings = 'os', 'arch', 'build_type'
    commit = 'bc32e3c'
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
        folder = self.name

        self.output.info('Cloning repo: %s dest: %s commit: %s' % (self.url, folder, self.commit))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.commit)

        if self.settings.os == 'Macos':
            tools.replace_in_file(os.path.join(folder, 'common', 'vp9_level_stats.h'),
                "std::queue<std::pair<int64_t, int64_t>>",
                "std::queue<std::pair<int64_t, int64_t> >")
            tools.replace_in_file(os.path.join(folder, 'CMakeLists.txt'),
                "require_cxx_flag_nomsvc(\"-std=c++11\")",
                "add_cxx_flag_if_supported(-std=c++11 -fno-rtti -fno-exceptions)")

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)

        cmake.definitions['ENABLE_TESTS'] = 'OFF'
        cmake.definitions['ENABLE_IWYU'] = 'OFF'
        cmake.definitions['CMAKE_VERBOSE_MAKEFILE'] = 'ON'

        cmake.configure(source_folder=self.name)

        # conan doesn't support properly switching runtimes at the moment,
        # need to use this hack in the meantime
        if self.settings.os == 'Windows':
            tools.replace_in_file('CMakeCache.txt', '/MD', '/MT', strict=False)
            cmake.configure(source_folder=self.name)

        cmake.build()

    def package(self):
        if self.settings.os == 'Windows':
            self.copy('*webm.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)
            self.copy('*.so', dst='lib', keep_path=False)
            self.copy('*.dylib', dst='lib', keep_path=False)
        self.copy('*.h', src='libwebm/common', dst='include/common', keep_path=False)
        self.copy('*.h', src='libwebm/mkvmuxer', dst='include/mkvmuxer', keep_path=False)
        self.copy('*.h', src='libwebm/mkvparser', dst='include/mkvparser', keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
