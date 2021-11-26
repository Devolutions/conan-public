from conans import ConanFile, python_requires, tools
import os, platform, subprocess, shutil, stat, json, re

def runner_logger(msg):
    if isinstance(msg, list):
        msg = (' ').join(msg)

    msg = 'Running: %s' % msg
    msg_length = len(msg)
    if msg_length > 80:
        msg_length = 80

    print('-' * msg_length)
    print(msg)
    print('-' * msg_length)

def execute_command(cmd, cwd=None, verbose=True):
    if isinstance(cmd, str):
        cmd = cmd.split()

    if verbose:
        runner_logger(cmd)
        output = None
    else:
        output = open(os.devnull, 'w')

    try:
        return subprocess.check_call(
            cmd,
            stdout=output,
            stderr=output,
            cwd=cwd
        )
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        exit(1)

def get_cmd_output(cmd, cwd=None, verbose=True, shell=False):
    if verbose:
        runner_logger(cmd)

    if isinstance(cmd, str):
        cmd = cmd.split()

    return subprocess.check_output(
        cmd,
        universal_newlines=True,
        cwd=cwd
    )

def load_file(path):
    with open(path, 'rb') as handle:
        tmp = handle.read()
        return tmp.decode("utf-8", "ignore")

def load_dotenv_file(filename):
    file = load_file(filename)
    return dict(line.split("=", 1) for line in file.splitlines())

class UtilsBase(object):
    def build_requirements(self):
        self.output.info("injecting build requirements!")

        self.build_requires('cbake/latest@devolutions/stable')

        target_os = self.get_target_os()

        if target_os == 'Linux':
            self.build_requires('sysroot/latest@devolutions/stable')

    def get_target_os(self):
        try:
            if self.settings.os:
                return str(self.settings.os)
        except:
            pass

        try:
            if self.settings.os_build:
                return str(self.settings.os_build)
        except:
            pass

        return None

    def get_target_arch(self):
        try:
            if self.settings.arch:
                return str(self.settings.arch)
        except:
            pass

        try:
            if self.settings.arch_build:
                return str(self.settings.arch_build)
        except:
            pass

        return None

    def get_target_distro(self):
        try:
            if self.settings.distro:
                return str(self.settings.distro)
        except:
            pass

        return None

    def cmake_wrapper(self, cmake, settings, options):
        cbake_home = self.deps_env_info["cbake"].CBAKE_HOME
        cmake.definitions['BUILD_SHARED_LIBS'] = options.shared
        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = options.fPIC

        target_os = self.get_target_os()
        target_arch = self.get_target_arch()

        try:
            if settings.os.version:
                os_version = str(settings.os.version)
        except:
            if target_os == "Macos":
                if target_arch == "x86_64":
                    os_version = "10.12"
                else:
                    os_version = "10.15"
            elif target_os == "iOS":
                os_version = "9.3"

        if target_os == 'Windows':
            cmake.generator = 'Visual Studio 17 2022'
            cmake.generator_platform = {
                'x86': 'Win32',
                'x86_64': 'x64',
                'armv7': 'ARM',
                'armv8': 'ARM64', # conan uses armv8 instead of arm64
                'arm64': 'ARM64'  # add arm64 to list just for safety
            }[target_arch]
        elif target_os == 'Macos':
            osx_arch = { 'x86_64': 'x86_64', 'armv8': 'arm64', 'universal': 'universal' }[target_arch]
            cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = os_version
            cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = osx_arch
            cmake.generator = 'Ninja'
        elif target_os == 'Linux':
            cmake.generator = 'Ninja'
            try:
                cmake.definitions['CMAKE_SYSROOT'] = self.deps_env_info["sysroot"].CMAKE_SYSROOT
                cmake.definitions['CMAKE_TOOLCHAIN_FILE'] = os.path.join(cbake_home, 'cmake', 'linux.toolchain.cmake')
            except:
                pass
        elif target_os == 'iOS':
            ios_arch = { 'x86': 'i386', 'x86_64': 'x86_64', 'armv8': 'arm64', 'armv7': 'armv7', 'universal': 'universal' }[target_arch]
            cmake.definitions['CMAKE_TOOLCHAIN_FILE'] = os.path.join(cbake_home, 'cmake', 'ios-%s.toolchain.cmake' % ios_arch)
            cmake.definitions['IOS_DEPLOYMENT_TARGET'] = os_version
            cmake.generator = 'Ninja'
        elif target_os == 'Android':
            abi = {'armv7': 'armeabi-v7a with NEON', 'armv8': 'arm64-v8a', 'x86': 'x86', 'x86_64': 'x86_64'}[target_arch]
            conan_to_cbake_map = { 'x86': 'x86', 'x86_64': 'x86_64', 'armv7': 'arm', 'armv8': 'arm64'}[target_arch]

            cmake.definitions['CMAKE_TOOLCHAIN_FILE'] = os.path.join(cbake_home, 'cmake', 'android-%s.toolchain.cmake' % conan_to_cbake_map)
            cmake.definitions['ANDROID_PLATFORM'] = 'android-%s' % settings.os.api_level
            cmake.definitions['ANDROID_TOOLCHAIN'] = 'clang'
            cmake.definitions['ANDROID_ABI'] = abi

            if not 'ANDROID_NDK' in os.environ:
                if 'ANDROID_HOME' in os.environ:
                    os.environ['ANDROID_NDK'] = os.path.join(os.environ['ANDROID_HOME'], 'ndk-bundle')

            if not 'ANDROID_NDK' in os.environ:
                raise Exception('ANDROID_NDK environment variable is not set!')

            android_ndk = os.environ['ANDROID_NDK']
            cmake.definitions['ANDROID_NDK'] = android_ndk
            cmake.generator = 'Ninja'

    # lipo helper

    def lipo_create(self, output_dir):
        lib_files, inc_files, paths = self.lipo_detect_files(self)

        self.output.info('Copying headers to build directory')
        for file in inc_files:
            src_path = paths[0]
            src_file = os.path.expanduser(os.path.join(src_path, file))

            if not os.path.isfile(src_file):
                raise RuntimeError('%s does not exist' % src_file)

            dest_file = os.path.expanduser(os.path.join(output_dir, file))

            dir = os.path.dirname(dest_file)
            if not os.path.isdir(dir):
                tools.mkdir(dir)

            self.output.info('%s => %s' % (src_file, dest_file))
            shutil.copy(src_file, dest_file)

        for file in lib_files:
            self.output.info('Generating universal binary for %s' % file)

            output_file = os.path.join(output_dir, file)

            dir = os.path.dirname(output_file)
            if not os.path.isdir(dir):
                tools.mkdir(dir)

            cmd = 'lipo -create -output %s ' % output_file

            include_files = []
            for path in paths:
                lib_file = os.path.expanduser(os.path.join(path, file))
                if not os.path.isfile(lib_file):
                    raise RuntimeError('Expected file %s does not exist.' % lib_file)

                include_files.append(lib_file)

            cmd += ' '.join(include_files)

            execute_command(cmd)

            expected_archs = ['x86_64', 'arm64', 'armv7']
            self.lipo_validate(self, output_file, expected_archs)

    def lipo_detect_files(self):
        paths = []
        for package_id in self.lipo_get_packages_ids(self):
            params = (base_dir, self.name, self.version, self.user, self.channel, package_id)
            paths.append('%s/data/%s/%s/%s/%s/package/%s' % params)

        lib_files = []
        inc_files = []

        for path in paths:
            os.chdir(os.path.expanduser(path))
            for file in glob.glob('**/*.a', recursive=True):
                if file not in lib_files:
                    lib_files.append(file)

            for file in glob.glob('**/*.h', recursive=True):
                if file not in inc_files:
                    inc_files.append(file)

        return lib_files, inc_files, paths

    def lipo_get_package_name(self):
        return '%s/%s@%s/%s' % (self.name, self.version, self.user, self.channel)

    def lipo_get_packages_ids(self):
        conan_ios_architectures = ['x86_64', 'armv8', 'armv7']

        arches = ''
        for arch in conan_ios_architectures[:-1]:
            arches += 'arch=%s OR ' % arch
        arches += 'arch=%s' % conan_ios_architectures[-1]

        query = 'os=iOS AND build_type=%s AND (%s)' % (self.settings.build_type, arches)

        cmd = [
            'conan',
            'search',
            '%s' % self.lipo_get_package_name(self),
            '-q',
            query
        ]
        output = get_cmd_output(cmd)

        regex = re.compile(r"(.*)Package_ID: [a-z0-9]{40}")
        package_ids = []

        for line in output.split("\n"):
            if re.match(regex, line):
                package_ids.append(line.split()[-1])

        if len(package_ids) != len(conan_ios_architectures):
            raise RuntimeError('Expected %s package IDs, discovered %s' % (len(conan_ios_architectures), len(package_ids)))

        self.output.info('Discovered package IDs: %s' % package_ids)

        return package_ids

    def lipo_validate(self, file, expected_archs):
        self.output.info("Testing %s to ensure it's a universal binary" % file)
        self.output.info('Expected architectures: %s' % expected_archs)

        cmd = 'lipo %s -info' % file
        output = os.popen(cmd).read().rstrip()

        detected_archs = output.split('are:')[1].split()

        errors = 0

        for arch in expected_archs:
            if arch in detected_archs:
                self.output.info('%s: ok' % arch)
            else:
                self.output.error('%s: error' % arch)
                errors += 1

        if errors != 0:
            params = (', '.join(expected_archs), ', '.join(detected_archs))
            err = 'Expected the following architures %s detected %s' % params
            raise RuntimeError(err)

    def strip_binary(self, filename):
        strip_tool = tools.which("llvm-strip")
        if strip_tool is None:
            strip_tool = tools.which("strip")
        if self.settings.os == 'Linux' or self.settings.os == 'Android':
            execute_command('%s -s %s' % (strip_tool, filename))
        elif self.settings.os == 'Macos':
            execute_command('%s %s' % (strip_tool, filename))

    # cargo/rustup helper

    def get_cargo_cbake_env(self):
        cbake_home = self.deps_env_info["cbake"].CBAKE_HOME
        target_os = self.get_target_os()
        target_arch = self.get_target_arch()
        target_distro = self.get_target_distro()
        target_env = {}
        if target_os == 'Linux':
            cmake_generator = 'Ninja'
            try:
                cmake_sysroot = self.deps_env_info["sysroot"].CMAKE_SYSROOT
                cmake_toolchain_file = os.path.join(cbake_home, 'cmake', 'linux.toolchain.cmake')
                cargo_cbake_name = "%s-%s" % (target_distro, target_arch)
                cmake_source_dir = os.path.join(cbake_home, 'cargo')
                cmake_binary_dir = os.path.join(self.build_folder, "cargo-cbake-%s" % (cargo_cbake_name))
                cargo_cbake_dir = cmake_binary_dir
                execute_command("cmake -G %s -S %s -B %s -DCMAKE_SYSROOT=%s "
                    "-DCMAKE_TOOLCHAIN_FILE=%s -DCARGO_CBAKE_DIR=%s -DCARGO_CBAKE_NAME=%s" % (
                    cmake_generator,
                    cmake_source_dir,
                    cmake_binary_dir,
                    cmake_sysroot,
                    cmake_toolchain_file,
                    cargo_cbake_dir,
                    cargo_cbake_name), verbose=True)
                cargo_dotenv_file = os.path.join(cargo_cbake_dir, "%s.env" % (cargo_cbake_name))
                target_env = load_dotenv_file(cargo_dotenv_file)
                return target_env
            except:
                pass
        return target_env

    def cargo_build(self, target=None, build_type=None, verbose=False, args=None):
        self.rustup_validate(target)
        execute_command('cargo clean')

        cmd = 'cargo build'
        cmd += ' --target %s' % target

        if args:
            cmd += ' %s' % args

        if build_type == 'Release':
            cmd += ' --release'

        if verbose:
            cmd += ' -vvv'

        execute_command(cmd)

    def rustup_install(self, target, component):
        if component == 'toolchain':
            target = 'stable-%s' % target

        execute_command('rustup %s install %s' % (component, target))

    def rustup_is_installed(self, target, component):
        if component == 'target':
            components = get_cmd_output('rustup target list').splitlines()
        elif component == 'toolchain':
            target = 'stable-%s' % target
            components = get_cmd_output('rustup toolchain list').splitlines()
        else:
            raise Exception('Invalid component: %s' % component)

        installed_components = []
        regex = re.compile(r'(installed|default)')

        for each in components:
            if regex.search(each):
                installed_components.append(each.split(' ')[0])

        if target in installed_components:
            return True
        else:
            return False

    def get_cargo_target(self):
        target_os = self.get_target_os()
        target_arch = self.get_target_arch()
        if target_os == 'Macos':
            if target_arch == 'armv8':
                return 'aarch64-apple-darwin'
            elif target_arch == 'x86_64':
                return 'x86_64-apple-darwin'
        elif target_os == 'Linux':
            if target_arch == 'armv8':
                return 'aarch64-unknown-linux-gnu'
            elif target_arch == 'x86_64':
                return 'x86_64-unknown-linux-gnu'
            elif target_arch == 'x86':
                return 'i686-unknown-linux-gnu'
        elif target_os == 'Windows':
            if target_arch == 'armv8':
                return 'aarch64-pc-windows-msvc'
            elif target_arch == 'x86_64':
                return 'x86_64-pc-windows-msvc'
            elif target_arch == 'x86':
                return 'i686-pc-windows-msvc'

        raise Exception('Received invalid parameters, cannot determine target! (os: %s arch: %s)' % (target_os, target_arch))

    def rustup_validate(self, target):
        if not self.rustup_is_installed(target, 'target'):
            self.rustup_install(target, 'target')

class SharedUtils(ConanFile):
    name = "shared"
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
