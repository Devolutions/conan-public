from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import copy, get, load
import os


class WpeWebKitConan(ConanFile):
    name = "wpewebkit"
    exports = "VERSION"
    license = "LGPL-2.1-or-later AND BSD-2-Clause"
    url = "https://wpewebkit.org/releases"
    description = "WPE WebKit browser engine, built for the legacy libwpe/WPEBackend-fdo API"
    settings = "os", "arch", "build_type"
    python_requires = "shared/1.0.0@devolutions/stable"
    python_requires_extend = "shared.UtilsBase"

    options = {
        # The 2.0 WPE Platform API (wpe_display_*, wpe_toplevel_*, plus the DRM and
        # Wayland backends). Avalonia's WpeWebViewAdapter does not call a single symbol
        # of it, and enabling it drags in libinput, libevdev, libmtdev, libwacom,
        # libhidapi-hidraw, libudev and the wayland chain as runtime dependencies.
        "wpe_platform": [True, False],
        # Speech synthesis (libflite and its 6 voice/lexicon libraries), gamepad
        # (libmanette, which WebXR depends on), spellcheck (libenchant-2) and the
        # WebDriver binary. All default ON for the WPE port; all unused by RDM.
        "optional_features": [True, False],
        # Honour WEBKIT_EXEC_PATH at runtime instead of baking the install prefix in.
        # Required for a relocatable bundle; see the comment in validate().
        "developer_mode": [True, False],
    }
    default_options = {
        "wpe_platform": False,
        "optional_features": False,
        "developer_mode": True,
    }

    def set_version(self):
        self.version = load(self, os.path.join(self.recipe_folder, "VERSION")).strip()

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("wpewebkit is only supported for Linux targets")

    def requirements(self):
        # Both are runtime dependencies as well as build ones: the consumer dlopens
        # libwpe-1.0.so.1 and libWPEBackend-fdo-1.0.so.1 by bare name before it will
        # use WPE at all.
        self.requires("libwpe/1.16.0@devolutions/stable")
        self.requires("wpebackend-fdo/1.16.0@devolutions/stable")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, f"{self.url}/{self.name}-{self.version}.tar.xz", strip_root=True)

    def generate(self):
        # find_package(WPE) and FindWPEBackendFDO.cmake both resolve through
        # pkg-config (modules wpe-1.0 and wpebackend-fdo-1.0).
        PkgConfigDeps(self).generate()

        optional = bool(self.options.optional_features)

        tc = CMakeToolchain(self)
        self.apply_linux_sysroot(tc)
        tc.variables["PORT"] = "WPE"
        tc.variables["DEVELOPER_MODE"] = bool(self.options.developer_mode)
        # ENABLE_WPE_LEGACY_API is the reason this package exists: it is what compiles
        # UIProcess/API/wpe/WebKitWebViewBackend.cpp, and therefore the only way
        # libWPEWebKit-2.0.so.1 exports webkit_web_view_backend_new(). The soname stays
        # 2.0 regardless, because the API version is chosen by ENABLE_WPE_1_1_API.
        tc.variables["ENABLE_WPE_LEGACY_API"] = True
        tc.variables["ENABLE_WPE_PLATFORM"] = bool(self.options.wpe_platform)
        tc.variables["ENABLE_SPEECH_SYNTHESIS"] = optional
        tc.variables["ENABLE_GAMEPAD"] = optional
        tc.variables["ENABLE_SPELLCHECK"] = optional
        tc.variables["ENABLE_WEBDRIVER"] = optional
        # Test harnesses and developer tooling. ENABLE_API_TESTS, ENABLE_LAYOUT_TESTS,
        # ENABLE_JSC_RESTRICTED_OPTIONS_BY_DEFAULT, ENABLE_WPE_QT_API, ENABLE_THUNDER and
        # CLANGD_AUTO_SETUP all default to ${ENABLE_DEVELOPER_MODE}, so DEVELOPER_MODE
        # above silently turns them on unless each is switched back off here.
        tc.variables["ENABLE_MINIBROWSER"] = False
        tc.variables["ENABLE_API_TESTS"] = False
        tc.variables["ENABLE_LAYOUT_TESTS"] = False
        tc.variables["ENABLE_JSC_RESTRICTED_OPTIONS_BY_DEFAULT"] = False
        tc.variables["ENABLE_WPE_QT_API"] = False
        tc.variables["ENABLE_THUNDER"] = False
        tc.variables["CLANGD_AUTO_SETUP"] = False
        tc.variables["ENABLE_INTROSPECTION"] = False
        tc.variables["ENABLE_DOCUMENTATION"] = False
        # Debian and Ubuntu ship the WOFF2 CLI tool but no pkg-config dev package.
        tc.variables["USE_WOFF2"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        lib = os.path.join(self.build_folder, "lib", "libWPEWebKit-2.0.so.1")
        if not os.path.exists(lib):
            raise ConanInvalidConfiguration(
                f"{lib} was not produced; check ENABLE_WPE_1_1_API, which selects the soname")

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # Deliberately no cpp_info.libs: nothing links WPE. It is loaded at runtime with
        # dlopen, and the consumer also needs the helper executables and the injected
        # bundle, so what matters is the paths rather than a link line.
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = [os.path.join("include", "wpe-webkit-2.0")]
        self.cpp_info.bindirs = [os.path.join("libexec", "wpe-webkit-2.0")]

        # The three env vars a host process must export before the first web view. Set
        # here so a consumer can read them off the package instead of rediscovering them.
        self.runenv_info.define_path("WEBKIT_EXEC_PATH", os.path.join(self.package_folder, "libexec", "wpe-webkit-2.0"))
        self.runenv_info.define_path(
            "WEBKIT_INJECTED_BUNDLE_PATH",
            os.path.join(self.package_folder, "lib", "wpe-webkit-2.0", "injected-bundle"))
        self.runenv_info.append_path("LD_LIBRARY_PATH", os.path.join(self.package_folder, "lib"))
