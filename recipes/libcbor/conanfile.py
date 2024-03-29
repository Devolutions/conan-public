from conans import ConanFile, tools, CMake, python_requires
import os

class LibcborConan(ConanFile):
    name = 'libcbor'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'MIT'
    url = 'https://github.com/pjk/libcbor'
    description = 'libcbor'
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

    def build_requirements(self):
        super().build_requirements()

    def source(self):
        folder = self.name
        self.output.info('Cloning repo: %s dest: %s branch: %s' % (self.url, folder, self.branch))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(self.branch)

        tools.replace_in_file(os.path.join(folder, 'CMakeLists.txt'),
            "cmake_minimum_required(VERSION 3.0)",
            "cmake_minimum_required(VERSION 3.9)")

        tools.replace_in_file(os.path.join(folder, 'CMakeLists.txt'),
            "set(use_lto FALSE)",
            "set(use_lto TRUE)")

        tools.replace_in_file(os.path.join(folder, 'CMakeLists.txt'),
            "    check_ipo_supported(RESULT use_lto)",
            "    #check_ipo_supported(RESULT use_lto)")

    def build(self):
        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        
        cmake.definitions['SANITIZE'] = 'OFF'
        cmake.definitions['WITH_TESTS'] = 'OFF'
        cmake.definitions['WITH_EXAMPLES'] = 'OFF'

        cmake.configure(source_folder=self.name)
        cmake.build()
        cmake.install()

    def package(self):
        return

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
