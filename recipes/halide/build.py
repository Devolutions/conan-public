#!/usr/bin/env python3

import argparse
import platform as pf

from cpt.packager import ConanMultiPackager

def build_target(platform, arch, settings={}):
    builder = ConanMultiPackager(
        username = 'devolutions',
        build_policy = 'outdated',
        exclude_vcvars_precommand = True
    )

    build_types = ['Release']
    if debug:
        build_types.append('Debug')

    for build_type in build_types:
        builder.add(settings={'os_build': os_build(), 'arch_build': os_arch(), 'build_type': build_type})
    builder.run('%s-%s' % (platform, arch))

def os_arch():
    archi = pf.architecture()[0]

    if archi == '32bit':
        return 'x86'
    elif archi == '64bit':
        return 'x86_64'

def os_build():
    os = pf.system()

    if os == 'Darwin':
        return 'Macos'
    else:
        return os

def parse_cli():
    parser = argparse.ArgumentParser(description='conan packages build automator')
    parser.add_argument('-a', dest='architecture', metavar='arch',
                        help='architecture to build')
    parser.add_argument('--debug', dest='debug', help='generate Debug packages', action='store_true')
    parser.add_argument('-p', required=True, dest='platform', metavar='platform',
                        help='platform to build (required)')

    return parser.parse_args()


def architectures_map():
    return {
        'android': ['arm', 'arm64', 'x86', 'x86_64'],
        'linux': ['x86_64'],
        'ios': ['x86_64', 'armv7', 'arm64', 'universal'],
        'macos': ['x86_64', 'arm64'],
        'windows': ['x86', 'x86_64']
    }

def validate(platform, arch):
    map = architectures_map()

    if platform and platform not in map:
        print('invalid platform: %s. Supported platforms: %s' %
              (platform, list(map)))
        exit(1)

    if arch and platform and arch not in map[platform]:
        print('invalid architecture for %s: %s. Supported architectures: %s' %
              (platform, arch, map[platform]))
        exit(1)

if __name__ == '__main__':
    args = parse_cli()

    architecture = args.architecture
    debug = args.debug
    platform = args.platform

    validate(platform, architecture)

    if architecture:
        build_target(platform, architecture)
    else:
        for arch in architectures_map()[platform]:
            build_target(platform, arch)
