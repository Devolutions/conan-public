from conans import ConanFile, python_requires, tools
import os, glob, re, shutil

utils = python_requires('utils/latest@devolutions/stable')
expected_archs = ['x86_64', 'arm64', 'armv7']

def create(self, output_dir):
    lib_files, inc_files, paths = detect_files(self)

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

        utils.execute(cmd)

        validate(self, output_file, expected_archs)

def detect_files(self):
    paths = get_packages_paths(self)

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

def get_package_name(self):
    return '%s/%s@%s/%s' % (self.name, self.version, self.user, self.channel)

def get_packages_ids(self):
    conan_ios_architectures = ['x86_64', 'armv8', 'armv7']

    arches = ''
    for arch in conan_ios_architectures[:-1]:
        arches += 'arch=%s OR ' % arch
    arches += 'arch=%s' % conan_ios_architectures[-1]

    query = 'os=iOS AND build_type=%s AND (%s)' % (self.settings.build_type, arches)

    cmd = [
        'conan',
        'search',
        '%s' % get_package_name(self),
        '-q',
        query
    ]
    output = utils.get_cmd_output(cmd)

    regex = re.compile(r"(.*)Package_ID: [a-z0-9]{40}")
    package_ids = []

    for line in output.split("\n"):
        if re.match(regex, line):
            package_ids.append(line.split()[-1])

    if len(package_ids) != len(conan_ios_architectures):
        raise RuntimeError('Expected %s package IDs, discovered %s' % (len(conan_ios_architectures), len(package_ids)))

    self.output.info('Discovered package IDs: %s' % package_ids)

    return package_ids

def get_packages_paths(self, base_dir = '~/.conan'):
    paths = []
    for package_id in get_packages_ids(self):
        params = (base_dir, self.name, self.version, self.user, self.channel, package_id)
        paths.append('%s/data/%s/%s/%s/%s/package/%s' % params)

    return(paths)

def validate(self, file, expected_archs):
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

class Lipo(ConanFile):
    name = 'lipo'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
