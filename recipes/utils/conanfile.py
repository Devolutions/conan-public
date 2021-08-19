from conans import ConanFile, python_requires, tools
import os, platform, subprocess, shutil, stat, json

cbake_version = 'cbake/latest@devolutions/stable'
python_requires(cbake_version)

def cmake_wrapper(cmake, settings, options):
    execute('conan install %s' % cbake_version)

    cbake_root = package_info(cbake_version)['package_folder']
    cmake.definitions['BUILD_SHARED_LIBS'] = options.shared
    cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = options.fPIC

    # need to catch the exception and split conditions in 2 chunks
    # because conan raises if you try to access os or os_build and
    # it's not present in the object
    try:
        if settings.os:
            target = str(settings.os)
            arch = str(settings.arch)
    except:
        pass

    try:
        if settings.os_build:
            target = str(settings.os_build)
            arch = str(settings.arch_build)
    except:
        pass

    if target == 'Windows':
        cmake.generator = 'Visual Studio 16 2019'
        cmake.generator_platform = {
            'x86': 'Win32',
            'x86_64': 'x64',
            'armv7': 'ARM',
            'armv8': 'ARM64', # conan uses armv8 instead of arm64
            'arm64': 'ARM64'  # add arm64 to list just for safety
        }[str(arch)]
    elif target == 'Macos':
        osx_arch = { 'x86_64': 'x86_64', 'armv8': 'arm64', 'universal': 'universal' }[str(arch)]
        cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = settings.os.version
        cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = osx_arch
    elif target == 'iOS':
        ios_arch = { 'x86': 'i386', 'x86_64': 'x86_64', 'armv8': 'arm64', 'armv7': 'armv7', 'universal': 'universal' }[str(arch)]

        cmake.definitions['CMAKE_TOOLCHAIN_FILE'] = os.path.join(cbake_root, 'ios-%s.toolchain.cmake' % ios_arch)
        cmake.definitions['IOS_DEPLOYMENT_TARGET'] = settings.os.version
    elif target == 'Android':
        if not 'ANDROID_HOME' in os.environ:
            raise Exception('You need to set the ANDROID_HOME environment variable')

        abi = {'armv7': 'armeabi-v7a with NEON', 'armv8': 'arm64-v8a', 'x86': 'x86', 'x86_64': 'x86_64'}[str(arch)]
        conan_to_cbake_map = { 'x86': 'x86', 'x86_64': 'x86_64', 'armv7': 'arm', 'armv8': 'arm64'}[str(arch)]

        cmake.definitions['CMAKE_TOOLCHAIN_FILE'] = os.path.join(cbake_root, 'android-%s.toolchain.cmake' % conan_to_cbake_map)
        cmake.definitions['ANDROID_PLATFORM'] = 'android-%s' % settings.os.api_level
        cmake.definitions['ANDROID_ABI'] = abi

        if not 'ANDROID_NDK' in os.environ:
            ndk_path = os.path.join(os.environ['ANDROID_HOME'], 'ndk-bundle')
        else:
            ndk_path = os.environ['ANDROID_NDK']

        cmake.definitions['ANDROID_NDK'] = ndk_path

def compress(src, dst):
    print('Finding 7z executable')
    bin = get_7z_bin()

    print("Compressing: src: %s dst: %s" % (src, dst))
    execute('%s a %s %s' % (bin, dst, src))

def create_artifacts_dir(build_dir, build_os, build_arch):
    artifacts_dir = os.path.join(build_dir, '..', '..', 'artifacts')
    artifacts_dir = os.path.join(artifacts_dir, str(build_os), str(build_arch))
    artifacts_dir = os.path.abspath(artifacts_dir)

    if not os.path.isdir(artifacts_dir):
        print('Creating artifacts directory: %s' % artifacts_dir)
        os.makedirs(artifacts_dir)

    return artifacts_dir

def decompress(src, dst):
    print('Finding 7z executable')
    bin = get_7z_bin()

    print("Decompressing: src: %s dst: %s" % (src, dst))
    execute('%s x -o%s %s' % (bin, dst, src))

def execute(cmd, cwd=None, verbose=True):
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

def extract_file_name(file):
    if platform.system() == 'Windows':
        return file.split('\\')[-1]
    else:
        return file.split('/')[-1]

def get_7z_bin():
    bin_dir = get_bin_dir('7z/1.1.1-1@devolutions/stable')

    exec = '7za'
    if platform.system() == 'Windows':
        exec += '.exe'

    return os.path.join(bin_dir, exec)

def get_bin_dir(package):
    cmd = 'conan info %s  --paths -n package_folder -pr %s' % (package, get_profile())
    bin_dir = get_cmd_output(cmd).splitlines()[1].split()[1]
    return os.path.join(bin_dir, 'bin')

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

def get_remote_version(repo):
    name = repo.split('/')[-1]
    name = name.split('.')[-2]

    try:
        execute('git clone -n --depth=1 %s' % repo, verbose=False)
        execute('git checkout HEAD VERSION', cwd=name, verbose=False)

        path = os.path.join(os.getcwd(), name, 'VERSION')
        return open(path, 'r').read().rstrip()
    finally:
        shutil.rmtree(name, onerror=remove_readonly)

def get_profile():
    build_host = platform.system()
    build_arch = platform.architecture()[0]

    if build_host == 'Darwin':
        profile = 'macos-x86_64'
    elif build_host == 'Windows':
        profile = 'windows-x86_64'
    elif build_host == 'Linux':
        if build_arch == '32bit':
            profile = 'linux-x86'
        else:
            profile = 'linux-x86_64'
    else:
        raise Exception('Unsupported system: %s' % build_host)

    return profile

def ios_toolchain_path():
    execute('conan install %s' % cbake_version)
    package_folder = package_info(cbake_version)['package_folder']
    toolchain = os.path.join(package_folder, 'ios.toolchain.cmake')

    if not os.path.isfile(toolchain):
        raise OSError('Toolchain file %s does not exists' % toolchain)

    return toolchain

def last_commit_id(url, ref, type='branch'):
    if platform.system() == 'Windows':
        bin = 'git.exe'
    else:
        bin = 'git'

    if type == 'branch':
        cmd = '%s ls-remote %s refs/heads/%s' % (bin, url, ref)
    elif type == 'tag':
        cmd = '%s ls-remote %s refs/tags/%s' % (bin, url, ref)
    else:
        raise Exception('Invalid type: %s' % type)

    output = get_cmd_output(cmd)
    if not output:
        raise Exception('Couldnt get last commit id.')

    return output.split()[0]

def package_info(package_name):
    cmd = 'conan info %s --paths -j' % package_name
    return json.loads(get_cmd_output(cmd, verbose=False))[0]

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

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

class Utils(ConanFile):
    name = 'utils'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
    license = 'MIT'
    description = "utils"
