from conans import ConanFile, tools, CMake, python_requires
import os, shutil

class LibUdevZeroConan(ConanFile):
    name = 'libudev-zero'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'ISC'
    url = 'https://github.com/illiliti/libudev-zero'
    description = 'libudev-zero'
    settings = 'os', 'arch', 'distro', 'build_type'
    no_copy_source = True
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    exports = ['VERSION',
        'patches/CMakeLists.txt',
        'patches/0001-fix-undefined-line-max-on-android.patch']

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
        tag = self.version
        self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, tag))
        git = tools.Git(folder=folder)
        git.clone(self.url)
        git.checkout(tag)

        patches_dir = os.path.join(self.recipe_folder, "patches")
        shutil.copy(os.path.join(patches_dir, "CMakeLists.txt"), os.path.join(folder, "CMakeLists.txt"))

        if os.path.isdir(patches_dir):
            for patch_file in [f for f in os.listdir(patches_dir) if f.endswith('.patch')]:
                patch_path = os.path.join(patches_dir, patch_file)
                self.output.info('Applying patch: %s' % patch_path)
                tools.patch(base_path=folder, patch_file=patch_path)

    def build(self):
        cmake = CMake(self)
        self.cmake_wrapper(cmake, self.settings, self.options)
        cmake.configure(source_folder=self.name)
        cmake.build()
        cmake.install()

    def package(self):
        return

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
