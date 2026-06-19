from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import load, replace_in_file
from conan.tools.scm import Git
import os


class OpenSSHConan(ConanFile):
    name = "openssh"
    exports = "VERSION"
    license = "BSD"
    url = "https://github.com/openssh/openssh-portable"
    description = "OpenSSH"
    settings = "os", "arch", "build_type"
    no_copy_source = False
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"
    use_prebuilt_msdeps = False

    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": True,
    }

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()

    def requirements(self):
        self.requires("zlib/1.3.1@devolutions/stable")
        self.requires("libcbor/0.10.2@devolutions/stable")
        self.requires("libressl/3.8.2@devolutions/stable")
        self.requires("libfido2/1.14.0@devolutions/stable")

    def layout(self):
        cmake_layout(self)

    def source(self):
        folder = self.name
        version_parts = self.version.split(".")
        self.branch = f"V_{version_parts[0]}_{version_parts[1]}_P1"
        self.output.info(f"Cloning repo: {self.url} dest: {folder} branch: {self.branch}")
        git = Git(self)
        git.clone(url=self.url, target=folder, args=["--branch", self.branch])

        Git(self).clone(url="https://github.com/Devolutions/openssh-distro", target="openssh-distro", args=["--branch", "master"])
        version_dir = f"v{self.version}"
        patches_dir = os.path.join(self.source_folder, "openssh-distro", "patches", version_dir)
        if os.path.isdir(patches_dir):
            patch_files = sorted([f for f in os.listdir(patches_dir) if f.endswith(".patch")])
            source_git = Git(self, folder=folder)
            for patch_file in patch_files:
                patch_path = os.path.join(patches_dir, patch_file)
                with open(patch_path, "r", encoding="utf-8", newline="") as file:
                    content = file.read().replace("\r\n", "\n")
                with open(patch_path, "w", encoding="utf-8", newline="\n") as file:
                    file.write(content)
                patch_path = patch_path.replace("\\", "/")
                source_git.run(f"apply --whitespace=nowarn {patch_path}")
        replace_in_file(
            self,
            os.path.join(self.source_folder, folder, "CMakeLists.txt"),
            'set(VC_INCLUDE_PATH "${WindowsSdkDir}include/${WINSDK_VERSION}/ucrt")',
            'set(VC_INCLUDE_PATH "$ENV{INCLUDE};${WindowsSdkDir}include/${WINSDK_VERSION}/ucrt")',
        )

    def generate(self):
        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)
        tc.variables["USE_PREBUILT_DEPS"] = False

        if self.settings.os == "Windows":
            tc.variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDebug" if self.settings.build_type == "Debug" else "MultiThreaded"

        zlib_path = self._cmake_path(self.dependencies["zlib"].package_folder)
        tc.variables["ZLIB_INCLUDE_DIR"] = f"{zlib_path}/include"
        tc.variables["ZLIB_LIBRARY_DIR"] = f"{zlib_path}/lib"

        libressl_path = self._cmake_path(self.dependencies["libressl"].package_folder)
        tc.variables["LIBRESSL_INCLUDE_DIR"] = f"{libressl_path}/include"
        tc.variables["LIBRESSL_LIBRARY_DIR"] = f"{libressl_path}/lib"

        libfido2_path = self._cmake_path(self.dependencies["libfido2"].package_folder)
        tc.variables["FIDO2_INCLUDE_DIR"] = f"{libfido2_path}/include"
        tc.variables["FIDO2_LIBRARY_DIR"] = f"{libfido2_path}/lib"

        libcbor_path = self._cmake_path(self.dependencies["libcbor"].package_folder)
        tc.variables["CBOR_INCLUDE_DIR"] = f"{libcbor_path}/include"
        tc.variables["CBOR_LIBRARY_DIR"] = f"{libcbor_path}/lib"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, self.name))
        cmake.build()
        cmake.install()

    @staticmethod
    def _cmake_path(path):
        return path.replace("\\", "/")
