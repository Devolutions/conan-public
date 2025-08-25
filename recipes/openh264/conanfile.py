from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.cmake import CMake, cmake_layout
import os, shutil, bz2, ssl
import urllib.request

class OpenH264Conan(ConanFile):
    name = 'openh264'

    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    description = 'Pre-built OpenH264 binaries'
    license = "BSD-2-Clause"
    url = 'https://github.com/cisco/openh264.git'
    tag = 'v%s' % version
    settings = 'os', 'arch', 'distro', 'build_type'
    python_requires = "shared/[1.0.0]@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    no_copy_source = True
    exports = ['VERSION']

    options = {
        'fPIC': [True, False],
        'shared': [True, False]
    }

    def layout(self):
        cmake_layout(self)
    default_options = {
        'fPIC': True,
        'shared': False
    }


    def layout(self):
        cmake_layout(self)
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
            git = Git(self, folder=folder)
            git.clone(url=self.url, target=".")
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

        filename = self.openh264_filename(self.version)
        extracted_path = os.path.join(self.source_folder, filename) 
        filename = '%s.bz2' % filename
        bz2_path = os.path.join(self.source_folder, filename)
        url = f"https://ciscobinary.openh264.org/{filename}"
        if os.path.exists(extracted_path):
            os.remove(extracted_path)

        # https://github.com/cisco/openh264/issues/909
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_REQUIRED

        with urllib.request.urlopen(url, context=context) as response, open(bz2_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        with bz2.BZ2File(bz2_path, "rb") as f_in:
            data = f_in.read()
            tools.save(extracted_path, data)

    def package(self):
        copy(self, '*.dll', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        copy(self, '*.so', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)
        copy(self, '*.dylib', dst=os.path.join(self.package_folder, 'lib'), src=self.build_folder)

        headers = os.path.join(self.source_folder, self.name, "codec", "api")
        copy(self, '*.h', src=os.path.join(self.source_folder, headers), dst=os.path.join(self.package_folder, 'include', keep_path=True))

    def package_info(self):
        self.cpp_info.libs = ["openh264"]
        self.user_info.version = str(self.version)
