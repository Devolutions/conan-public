from conans import ConanFile, tools, AutoToolsBuildEnvironment, python_requires

import os
import shutil
import subprocess

class LibvpxConan(ConanFile):
    name = 'libvpx'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'WebM'
    url = 'https://github.com/webmproject/libvpx.git'
    description = 'WebM VP8/VP9 Codec SDK'
    settings = 'os', 'arch', 'build_type'
    tag = 'v%s' % version
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    def build_requirements(self):
        if self.settings.os == 'Windows':
            self.build_requires('msys2/20210604@devolutions/stable')

    def source(self):
        if self.settings.arch == 'universal':
            return
        
        source_url = "https://github.com/webmproject/libvpx/archive/v%s.tar.gz" % self.version
        tools.get(source_url, sha256='85803ccbdbdd7a3b03d930187cb055f1353596969c1f92ebec2db839fa4f834a')
        extracted_dir = self.name + '-' + self.version
        os.rename(extracted_dir, 'sources')

        if self.settings.os == 'Windows':
            kits_root_10 = "C:\\Program Files (x86)\\Windows Kits\\10\\"
            platforms_uap_dir = os.path.join(kits_root_10, "platforms", "UAP")
            winsdk_versions = os.listdir(platforms_uap_dir)
            winsdk_versions.sort(reverse=True)
            winsdk_version = winsdk_versions[0]

            tools.replace_in_file("sources/build/make/gen_msvs_vcxproj.sh",
                "tag_content Keyword ManagedCProj",
                '''tag_content Keyword ManagedCProj
                tag_content WindowsTargetPlatformVersion %s''' % (winsdk_version))
            tools.replace_in_file("sources/configure",
                "-vs15", "-vs16")

    def build(self):
        if self.settings.arch == 'universal':
            self.lipo_create(self, self.build_folder)
            return

        if self.settings.os == 'Windows':
            self.msbuild_exe = subprocess.check_output("vswhere -latest -products * -requires Microsoft.Component.MSBuild -find MSBuild/**/Bin/MSBuild.exe",
                universal_newlines=True).splitlines()[0].rstrip().replace('\\\\', '\\')
            msbuild_path = tools.unix_path(os.path.dirname(self.msbuild_exe), tools.MSYS2)
            self.nasm_exe = "C:\\Program Files\\NASM\\nasm.exe"
            nasm_path_win32 = os.path.dirname(self.nasm_exe)
            nasm_path_msys2 = tools.unix_path(nasm_path_win32, tools.MSYS2)
            msys2_bin = self.deps_env_info["msys2"].MSYS_BIN
            with tools.environment_append({'PATH': [msbuild_path, nasm_path_win32, nasm_path_msys2],
                'CONAN_BASH_PATH': os.path.join(msys2_bin, 'bash.exe')}):
                self.build_configure()
        else:
            self.build_configure()

    def build_configure(self):
        os.chdir('sources')
        if self.settings.os == 'Windows':
            gen = os.path.join('build', 'make', 'gen_msvs_vcxproj.sh')
            tools.replace_in_file(gen,
                                    '        --help|-h) show_help',
                                    '        --help|-h) show_help\n        ;;\n        -O*) echo "ignoring -O..."\n')
            tools.replace_in_file(gen,
                                    '        --help|-h) show_help',
                                    '        --help|-h) show_help\n        ;;\n        -Zi) echo "ignoring -Zi..."\n')
            tools.replace_in_file(gen,
                                    '        --help|-h) show_help',
                                    '        --help|-h) show_help\n        ;;\n        -MT) echo "ignoring -MT..."\n')
            tools.replace_in_file(gen,
                                'tag_content WholeProgramOptimization true',
                                'tag_content WholeProgramOptimization false')

        win_bash = self.settings.os == 'Windows'
        prefix = os.path.abspath(self.package_folder)

        if self.settings.os == 'Windows':
            prefix = tools.unix_path(prefix, tools.MSYS2)

        args = [
            '--prefix=%s' % prefix,
            '--as=auto',
            '--enable-vp8-encoder',
            '--enable-libyuv',
            '--enable-webm-io',
            '--enable-static',
            '--disable-examples',
            '--disable-tools',
            '--disable-docs',
            '--disable-multithread',
            '--disable-shared',
            '--disable-unit-tests'
        ]

        if self.settings.build_type == 'Debug':
            args.append('--enable-debug')
            args.append('--enable-debug-libs')

        if not self.settings.os == 'Windows':
            args.append('--enable-pic')
        else:
            args.append('--enable-static-msvcrt')

        if self.settings.os == 'Macos':
            if self.settings.arch == 'x86_64':
                target = "x86_64-darwin13-gcc" # darwin 13 is macOS 10.9
            else:
                target = "arm64-darwin20-gcc"
        elif self.settings.os == 'Linux':
            if self.settings.arch == 'x86':
                target = "x86-linux-gcc"
            else:
                target = "x86_64-linux-gcc"
        elif self.settings.os == 'Windows':
            if self.settings.arch == 'x86':
                target = "x86-win32-vs16"
            elif self.settings.arch == 'x86_64':
                target = "x86_64-win64-vs16"
            else:
                target = "arm64-win64-vs16"

        args.append('--target=' + target)

        env_build = AutoToolsBuildEnvironment(self, win_bash=win_bash)
        env_build.configure(args=args, host=False, build=False, target=False)

        self.msvc_platform = { 'x86':'Win32',
            'x86_64':'x64', 'armv8':'ARM64'}[str(self.settings.arch)]

        if self.settings.os == 'Windows':
            env_build.make(args=['.projects'])
            subprocess.run([self.msbuild_exe, "vpx.sln", "/m", "/t:Build",
                "/p:Configuration=%s" % (self.settings.build_type),
                "/p:Platform=%s" % (self.msvc_platform)])
            env_build.make(args=['install'])
            if self.settings.build_type == 'Debug':
                vpx_lib = os.path.join(self.msvc_platform, 'Debug', 'vpxmtd.lib')
                libdir = os.path.join(self.package_folder, 'lib', self.msvc_platform)
                os.makedirs(libdir)
                shutil.copy(vpx_lib, os.path.join(libdir, 'vpxmt.lib'))
        else:
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        if self.settings.arch == 'universal':
            self.copy('*.a', dst='lib', keep_path=False)
            self.copy('*.h', src='include', dst='include')
            return

        pkgconfig_dir = os.path.join(self.package_folder, 'lib', 'pkgconfig')

        if os.path.isdir(pkgconfig_dir):
            shutil.rmtree(pkgconfig_dir)

        self.copy("*.h", src="include", dst="include")

        if self.settings.os == 'Windows':
            libdir = os.path.join(self.package_folder, 'lib', self.msvc_platform)
            shutil.move(os.path.join(libdir, 'vpxmt.lib'), os.path.join(self.package_folder, 'lib', 'vpx.lib'))
        else:
            self.copy("*.a", dst="lib")

    def package_info(self):
        self.cpp_info.libs = ['vpx']
