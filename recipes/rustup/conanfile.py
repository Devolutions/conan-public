from conans import ConanFile, python_requires
import os
import re

utils = python_requires('utils/latest@devolutions/stable')

def build(target=None, build_type=None, verbose=False, args=None):
    validate(target)

    clean()

    cmd = 'cargo build'
    cmd += ' --target %s' % target

    if args:
        cmd += ' %s' % args

    if build_type == 'Release':
        cmd += ' --release'

    if verbose:
        cmd += ' -vvv'

    utils.execute(cmd)

def clean():
    utils.execute('cargo clean')

def install(target, component):
    if component == 'toolchain':
        target = 'stable-%s' % target

    utils.execute('rustup %s install %s' % (component, target))

def is_installed(target, component):
    if component == 'target':
        components = utils.get_cmd_output('rustup target list').splitlines()
    elif component == 'toolchain':
        target = 'stable-%s' % target
        components = utils.get_cmd_output('rustup toolchain list').splitlines()
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

def target(os, arch):
    if os == 'Macos':
        if arch == 'armv8':
            return 'aarch64-apple-darwin'
        elif arch == 'x86_64':
            return 'x86_64-apple-darwin'
    elif os == 'Linux':
        if arch == 'armv8':
            return 'aarch64-unknown-linux-gnu'
        elif arch == 'x86_64':
            return 'x86_64-unknown-linux-gnu'
        elif arch == 'x86':
            return 'i686-unknown-linux-gnu'
    elif os == 'Windows':
        if arch == 'armv8':
            return 'aarch64-pc-windows-msvc'
        elif arch == 'x86_64':
            return 'x86_64-pc-windows-msvc'
        elif arch == 'x86':
            return 'i686-pc-windows-msvc'

    raise Exception('Received invalid parameters, cannot determine target! (os: %s arch: %s)' % (os, arch))

def validate(target):
    if not is_installed(target, 'target'):
        install(target, 'target')

    if not is_installed(target, 'toolchain'):
        install(target, 'toolchain')

class Rustup(ConanFile):
    name = 'rustup'
    exports = 'VERSION'
    version = open(os.path.join('.', 'VERSION'), 'r').read().rstrip()
