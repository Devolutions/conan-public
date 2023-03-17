from conans import ConanFile, tools, CMake, python_requires
import os

class MinizConan(ConanFile):
    name = 'cjson'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'MIT'
    url = 'https://github.com/DaveGamble/cJSON'
    description = 'cJSON: Ultralightweight JSON parser in ANSI C'
    settings = 'os', 'arch', 'distro', 'build_type'
    no_copy_source = True
    branch = 'v' + version
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
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.branch))
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
        cmake.definitions['ENABLE_CJSON_TEST'] = 'OFF'
        cmake.definitions['ENABLE_LOCALES'] = 'OFF'
        cmake.definitions['ENABLE_TARGET_EXPORT'] = 'OFF'
        cmake.definitions['ENABLE_CJSON_UNINSTALL'] = 'OFF'

        cmake.configure(source_folder=self.name)

        if self.settings.os == "Windows":
            tools.replace_in_file("CMakeCache.txt", '/MD', '/MT', strict = False)
            cmake.configure(source_folder=self.name)

        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.arch == 'universal':
            self.copy('*.a', dst='lib', keep_path=False)
            self.copy('*.h', src='include', dst='include')
            return

        if self.settings.os == 'Windows':
            self.copy('*.lib', dst='lib', keep_path=False)
        else:
            self.copy('*.a', dst='lib', keep_path=False)

        self.copy('*.h', dst='include', keep_path=False) # CMAKE_BINARY_DIR

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
