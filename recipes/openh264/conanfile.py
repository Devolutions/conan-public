from conans import ConanFile, CMake, tools, python_requires
import os, shutil
import bz2

class OpenH264Conan(ConanFile):
    name = 'openh264'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    description = 'Pre-built OpenH264 binaries'
    license = "BSD-2-Clause"
    url = 'https://github.com/cisco/openh264.git'
    tag = 'v%s' % version
    settings = 'os', 'arch', 'distro', 'build_type'
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    no_copy_source = True

    options = {
        'fPIC': [True, False],
        'shared': [True, False]
    }
    default_options = {
        'fPIC': True,
        'shared': False
    }

    def _openh264_filename(self):
        os_ = str(self.settings.os)
        arch = str(self.settings.arch)
        version = str(self.version)

        base_name = "libopenh264"
        ext = None
        platform = None

        if os_ == "Windows":
            base_name = "openh264"
            ext = "dll"
            if arch == "x86_64":
                platform = "win64"
            elif arch == "armv8":
                platform = "win-arm64"

        elif os_ == "Linux":
            ext = "so"
            if arch == "x86_64":
                platform = "linux64.8"
            elif arch == "armv8":
                platform = "linux-arm64.8"

        elif os_ == "Macos":
            ext = "dylib"
            if arch == "x86_64":
                platform = "mac-x64"
            elif arch == "armv8":
                platform = "mac-arm64"

        if not platform or not ext:
            raise ConanInvalidConfiguration(f"Unsupported platform/arch: {os_} {arch}")

        return f"{base_name}-{version}-{platform}.{ext}"

    def source(self):
        if self.settings.arch == 'universal':
            return

        folder = self.name

        if 'CONAN_SOURCES_PATH' in os.environ:
            conan_sources_path = os.environ['CONAN_SOURCES_PATH']
            sources_path = os.path.join(conan_sources_path, self.name)
            shutil.copytree(sources_path, self.name)
        else:
            self.output.info('Cloning repo: %s dest: %s tag: %s' % (self.url, folder, self.tag))
            git = tools.Git(folder=folder)
            git.clone(self.url)
            git.checkout(self.tag)
            self.output.info("Current commit: %s" % (git.get_commit()))

    def build(self):
        if self.settings.arch == 'universal':
            return

        exts = [".dll", ".dylib", ".so", ".bz2"]
        for filename in os.listdir(self.source_folder):
            fullpath = os.path.join(self.source_folder, filename)
            if os.path.isfile(fullpath) and any(filename.endswith(ext) for ext in exts):
                os.remove(fullpath)
                self.output.info(f"Removed: {filename}")

        filename = self._openh264_filename()
        extracted_path = os.path.join(self.source_folder, filename) 
        filename = '%s.bz2' % filename
        bz2_path = os.path.join(self.source_folder, filename)
        url = f"http://ciscobinary.openh264.org/{filename}"
        if os.path.exists(extracted_path):
            os.remove(extracted_path)
        tools.download(url, bz2_path)

        with bz2.BZ2File(bz2_path, "rb") as f_in:
            data = f_in.read()
            tools.save(extracted_path, data)

    def package(self):
        self.copy('*.dll', dst='lib', keep_path=False)
        self.copy('*.so', dst='lib', keep_path=False)
        self.copy('*.dylib', dst='lib', keep_path=False)

        headers = os.path.join(self.source_folder, self.name, "codec", "api", "wels")
        self.copy('*.h', src=headers, dst='include', keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["openh264"]
