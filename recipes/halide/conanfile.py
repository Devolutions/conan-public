from conans import ConanFile, tools, CMake, python_requires
import os
import shutil

class HalideConan(ConanFile):
    name = 'halide'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    tag = 'v%s' % (version)
    no_copy_source = True
    use_prebuilt = True
    license = 'Independent JPEG Group'
    license = 'BSD'
    url = 'https://github.com/Halide/Halide.git'
    description = 'a language for fast, portable data-parallel computation'
    settings = 'os_build', 'arch_build'
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
        if self.use_prebuilt:
            return

        self.build_requires('clang-llvm/12.0.1@devolutions/stable')
        if self.settings.os_build == 'Linux':
            self.build_requires('cbake/latest@devolutions/stable')
        else:
            super().build_requirements()

    def source(self):
        if self.use_prebuilt:
            self.pkg_version = self.version
            self.pkg_platform = {'Windows':'windows','Macos':'macos','Linux':'ubuntu-18.04'}[str(self.settings.os_build)]
            self.pkg_arch = {'x86_64':'x86_64','armv8':'aarch64'}[str(self.settings.arch_build)]
            self.pkg_ext = ".tar.xz"
            self.dir_name = "halide-%s-%s-%s" % (self.pkg_version, self.pkg_arch, self.pkg_platform)
            release_version = "2021.2.4"
            archive_name = "%s%s" % (self.dir_name, self.pkg_ext)
            base_url = "https://github.com/awakecoding/llvm-prebuilt/releases/download"
            download_url = "%s/v%s/halide-%s-%s-%s%s" % (base_url,
                release_version, self.pkg_version, self.pkg_arch, self.pkg_platform, self.pkg_ext)
            tools.download(download_url, archive_name)
        else:
            folder = self.name
            self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
            git = tools.Git(folder=folder)
            git.clone(self.url)
            git.checkout(self.tag)

    def build(self):
        if self.use_prebuilt:
            self.pkg_version = self.version
            self.pkg_platform = {'Windows':'windows','Macos':'macos','Linux':'ubuntu-18.04'}[str(self.settings.os_build)]
            self.pkg_arch = {'x86_64':'x86_64','armv8':'aarch64'}[str(self.settings.arch_build)]
            self.pkg_ext = ".tar.xz"
            self.dir_name = "halide-%s-%s-%s" % (self.pkg_version, self.pkg_arch, self.pkg_platform)
            archive_name = "%s%s" % (self.dir_name, self.pkg_ext)
            archive_path = os.path.join(self.source_folder, archive_name)
            tools.untargz(archive_path)
            shutil.move(self.dir_name, "install")
        else:
            if self.settings.os_build == 'Windows':
                cmake = CMake(self, build_type='Release')
                cmake.generator = 'Visual Studio 16 2019'
                cmake.generator_platform = "x64"
            else:
                cmake = CMake(self)

            cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
            cmake.definitions['WARNINGS_AS_ERRORS'] = 'OFF'
            cmake.definitions['BUILD_SHARED_LIBS'] = 'ON'
            cmake.definitions['WITH_TESTS'] = 'OFF'
            cmake.definitions['WITH_APPS'] = 'OFF'
            cmake.definitions['WITH_TUTORIALS'] = 'OFF'
            cmake.definitions['WITH_DOCS'] = 'OFF'
            cmake.definitions['WITH_UTILS'] = 'OFF'
            cmake.definitions['WITH_PYTHON_BINDINGS'] = 'OFF'
            cmake.definitions['TARGET_WEBASSEMBLY'] = 'OFF'
            cmake.definitions['LLVM_DIR'] = os.path.join(self.deps_cpp_info['clang-llvm'].rootpath, 'lib', 'cmake', 'llvm')

            install_prefix = os.path.join(self.build_folder, "install")
            cmake.definitions['CMAKE_INSTALL_PREFIX'] = install_prefix

            cmake.configure(source_folder=self.name)
            cmake.build()
            cmake.install()

    def package(self):
        if self.settings.os_build == 'Windows':
            self.copy(pattern="install/bin/*.dll", dst="lib", keep_path=False)
            self.copy(pattern="install/lib/*.lib", dst="lib", keep_path=False)
        elif self.settings.os_build == 'Macos':
            self.copy(pattern="install/lib/*.dylib", dst="lib", keep_path=False, symlinks=True)
        elif self.settings.os_build == 'Linux':
            self.copy(pattern="install/lib/*.so*", dst="lib", keep_path=False, symlinks=True)
        self.copy(pattern="install/include/*.h", dst="include", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
