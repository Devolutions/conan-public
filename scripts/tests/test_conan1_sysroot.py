import contextlib
import hashlib
import http.server
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import conans
from conans import tools
from conans.client.file_copier import FileCopier
from conans.client.output import ConanOutput
from conans.errors import ConanException
from conans.model.env_info import EnvInfo


ROOT = Path(__file__).resolve().parents[2]


@contextlib.contextmanager
def working_directory(path):
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def load_recipe(name):
    path = ROOT / 'conan1' / 'recipes' / name / 'conanfile.py'
    spec = importlib.util.spec_from_file_location('recipe_' + name, path)
    module = importlib.util.module_from_spec(spec)
    with working_directory(path.parent):
        spec.loader.exec_module(module)
    return module


sysroot = load_recipe('sysroot')
# Conan's loader supplies this legacy import when loading python_requires.
with patch.object(conans, 'python_requires', Mock(), create=True):
    shared = load_recipe('shared')


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class SysrootTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.build = self.root / 'build'
        self.package = self.root / 'package'
        self.release = self.root / 'release'
        for path in (self.build, self.package, self.release):
            path.mkdir()
        self.recipe = sysroot.Sysroot(ConanOutput(io.StringIO()), None)
        self.recipe.settings = SimpleNamespace(os='Linux', arch='armv8', distro='ubuntu-20.04')
        self.recipe.options = SimpleNamespace(**sysroot.Sysroot.default_options)
        self.recipe.folders.set_base_build(str(self.build))
        self.recipe.folders.set_base_package(str(self.package))
        self.recipe.env_info = EnvInfo()
        self.recipe.copy = FileCopier([str(self.build)], str(self.package))
        self.recipe.build_requires = Mock()
        self.name = self.recipe._sysroot_name()
        self.filename = self.name + '-sysroot.tar.xz'

    @contextlib.contextmanager
    def local_release(self):
        handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(self.release), **kwargs)
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        base_url = 'http://127.0.0.1:%s' % server.server_port
        prefix = 'https://github.com/Devolutions/CBake/releases/download/v2026.01.15.0'
        download, get = tools.download, tools.get

        def redirected_download(url, *args, **kwargs):
            self.assertTrue(url.startswith(prefix + '/'))
            return download(url.replace(prefix, base_url), *args, retry=0, **kwargs)

        def redirected_get(url, *args, **kwargs):
            self.assertTrue(url.startswith(prefix + '/'))
            return get(url.replace(prefix, base_url), *args, retry=0, **kwargs)

        try:
            with patch.object(tools, '_global_config', SimpleNamespace(retry=0, retry_wait=0, download_cache=None)), \
                    patch.object(tools, '_global_output', ConanOutput(io.StringIO())), \
                    patch.object(tools, 'download', side_effect=redirected_download), \
                    patch.object(tools, 'get', side_effect=redirected_get), \
                    working_directory(self.build):
                yield
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

    def archive(self, root=None):
        root = self.name if root is None else root
        with tarfile.open(self.release / self.filename, 'w:xz') as archive:
            for name in ('usr/include/stdio.h', 'usr/lib/libfixture.so.1'):
                data = b'fixture\n'
                member = tarfile.TarInfo(root + '/' + name)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
            link = tarfile.TarInfo(root + '/usr/lib/libfixture.so')
            link.type = tarfile.SYMTYPE
            link.linkname = 'libfixture.so.1'
            archive.addfile(link)
        self.checksum()

    def checksum(self, digest=None, filename=None):
        if digest is None:
            digest = hashlib.sha256((self.release / self.filename).read_bytes()).hexdigest().upper()
        (self.release / 'checksums').write_text('%s  %s\n' % (digest, filename or self.filename))

    def test_ci_matrix_names_and_defaults(self):
        self.assertEqual(self.recipe.options.source, 'prebuilt')
        self.assertEqual(self.recipe.options.release, 'v2026.01.15.0')
        for distro in ('ubuntu-18.04', 'ubuntu-20.04', 'ubuntu-22.04'):
            for arch, suffix in (('x86_64', 'amd64'), ('armv8', 'arm64')):
                with self.subTest(distro=distro, arch=arch):
                    self.recipe.settings.distro = distro
                    self.recipe.settings.arch = arch
                    self.assertEqual(self.recipe._sysroot_name(), distro + '-' + suffix)

    def test_prebuilt_package_and_shared_consumer(self):
        self.archive()
        self.recipe.build_requirements()
        self.recipe.build_requires.assert_not_called()
        with self.local_release(), patch.object(self.recipe, '_build_sysroot') as source_build:
            self.recipe.build()
            source_build.assert_not_called()
        self.recipe.package()
        self.recipe.package_info()
        expected = self.package / self.name
        self.assertEqual(self.recipe.env_info.CMAKE_SYSROOT, str(expected))
        self.assertTrue((expected / 'usr/include/stdio.h').is_file())
        self.assertTrue((expected / 'usr/lib/libfixture.so').is_symlink())
        self.assertEqual(os.readlink(expected / 'usr/lib/libfixture.so'), 'libfixture.so.1')
        consumer = shared.UtilsBase()
        consumer.settings = self.recipe.settings
        consumer.deps_env_info = {
            'cbake': SimpleNamespace(CBAKE_HOME='/cbake'),
            'sysroot': self.recipe.env_info,
        }
        cmake = SimpleNamespace(definitions={})
        consumer.cmake_wrapper(cmake, consumer.settings, SimpleNamespace(shared=False, fPIC=True))
        self.assertEqual(cmake.definitions['CMAKE_SYSROOT'], str(expected))
        self.assertEqual(cmake.definitions['CMAKE_TOOLCHAIN_FILE'], '/cbake/cmake/linux.toolchain.cmake')

    def test_checksum_formats(self):
        for marker in ('', '*'):
            with self.subTest(marker=marker):
                self.checksum('A' * 64, marker + self.filename)
                self.assertEqual(self.recipe._checksum_for(self.release / 'checksums', self.filename), 'a' * 64)

    def test_missing_or_malformed_checksum_stops_before_archive_download(self):
        for digest, filename, message in (
                ('A' * 64, 'other.tar.xz', 'No checksum found'),
                ('not-a-sha256', self.filename, 'Invalid SHA256'),
                ('A' * 63, self.filename, 'Invalid SHA256')):
            with self.subTest(digest=digest, filename=filename):
                self.checksum(digest, filename)
                with self.local_release(), patch.object(tools, 'get') as get:
                    with self.assertRaisesRegex(RuntimeError, message):
                        self.recipe.build()
                    get.assert_not_called()

    def test_checksum_mismatch_is_fatal(self):
        self.archive()
        self.checksum('0' * 64)
        with self.local_release(), patch.object(self.recipe, '_build_sysroot') as source_build:
            with self.assertRaisesRegex(ConanException, 'sha256'):
                self.recipe.build()
            source_build.assert_not_called()
        self.assertFalse((self.build / self.name / 'usr').exists())

    def test_corrupt_archive_is_fatal(self):
        (self.release / self.filename).write_bytes(b'not an xz archive')
        self.checksum()
        with self.local_release(), self.assertRaises(tarfile.ReadError):
            self.recipe.build()

    def test_retry_replaces_leftover_archive_after_failed_acquisition(self):
        (self.build / self.filename).write_bytes(b'partial download')
        (self.build / 'checksums').write_text('stale checksums')
        self.archive()
        with self.local_release():
            self.recipe.build()
        self.assertTrue((self.build / self.name / 'usr/include/stdio.h').is_file())
        self.assertFalse((self.build / self.filename).exists())

    def test_wrong_archive_layout_cannot_reuse_stale_sysroot(self):
        self.archive(root='unexpected')
        (self.build / self.name / 'usr').mkdir(parents=True)
        with self.local_release(), self.assertRaisesRegex(RuntimeError, 'missing expected directory'):
            self.recipe.build()

    def test_missing_release_files_are_fatal_without_source_fallback(self):
        for checksums_present in (False, True):
            with self.subTest(checksums_present=checksums_present):
                if checksums_present:
                    self.checksum('A' * 64)
                with self.local_release(), patch.object(self.recipe, '_build_sysroot') as source_build:
                    with self.assertRaises(ConanException):
                        self.recipe.build()
                    source_build.assert_not_called()

    def test_explicit_source_build_propagates_exit_139(self):
        self.recipe.options.source = 'build'
        self.recipe.deps_env_info = {'cbake': SimpleNamespace(CBAKE_HOME='/cbake')}
        self.recipe.build_requirements()
        self.recipe.build_requires.assert_called_once_with('cbake/latest@devolutions/stable')
        with patch.object(subprocess, 'run', side_effect=subprocess.CalledProcessError(139, 'pwsh')) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                self.recipe.build()
        run.assert_called_once_with(
            ['pwsh', '-File', '/cbake/build.ps1', 'sysroot',
             '-Distribution', 'ubuntu-20.04', '-Architecture', 'arm64',
             '-ExportPath', str(self.build / self.name), '-SkipPackaging'], check=True)
        with self.assertRaisesRegex(RuntimeError, 'missing expected directory'):
            self.recipe.package()

    def test_successful_source_process_must_produce_sysroot(self):
        self.recipe.options.source = 'build'
        self.recipe.deps_env_info = {'cbake': SimpleNamespace(CBAKE_HOME='/cbake')}
        (self.build / self.name / 'usr').mkdir(parents=True)
        with patch.object(subprocess, 'run'), self.assertRaisesRegex(RuntimeError, 'missing expected directory'):
            self.recipe.build()

    def test_source_build_packages_from_build_folder(self):
        self.recipe.options.source = 'build'
        self.recipe.deps_env_info = {'cbake': SimpleNamespace(CBAKE_HOME='/cbake')}

        def build(*args, **kwargs):
            (self.build / self.name / 'usr/include').mkdir(parents=True)
            (self.build / self.name / 'usr/include/stdio.h').write_text('fixture')

        with patch.object(subprocess, 'run', side_effect=build), patch.object(tools, 'download') as download:
            self.recipe.build()
            download.assert_not_called()
        self.recipe.package()
        self.assertTrue((self.package / self.name / 'usr/include/stdio.h').is_file())


if __name__ == '__main__':
    unittest.main()
