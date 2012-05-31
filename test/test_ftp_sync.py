# Copyright (C) 2007-2012, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# See the file LICENSE for licensing terms.

import ntpath
import os
import shutil
import StringIO
import sys
import unittest

import ftputil
from ftputil import ftp_sync


# Assume the test subdirectories are or will be in the current directory.
TEST_ROOT = os.getcwd()


class TestLocalToLocal(unittest.TestCase):

    def setUp(self):
        if not os.path.exists("test_empty"):
            os.mkdir("test_empty")
        if os.path.exists("test_target"):
            shutil.rmtree("test_target")
        os.mkdir("test_target")

    def test_sync_empty_dir(self):
        source = ftp_sync.LocalHost()
        target = ftp_sync.LocalHost()
        syncer = ftp_sync.Syncer(source, target)
        source_dir = os.path.join(TEST_ROOT, "test_empty")
        target_dir = os.path.join(TEST_ROOT, "test_target")
        syncer.sync(source_dir, target_dir)

    def test_source_with_and_target_without_slash(self):
        source = ftp_sync.LocalHost()
        target = ftp_sync.LocalHost()
        syncer = ftp_sync.Syncer(source, target)
        source_dir = os.path.join(TEST_ROOT, "test_source/")
        target_dir = os.path.join(TEST_ROOT, "test_target")
        syncer.sync(source_dir, target_dir)


# Helper classes for `TestUploadFromWindows`

class LocalWindowsHostPath(object):

    def __getattr__(self, name):
        return getattr(ntpath, name)


class LocalWindowsHost(ftp_sync.LocalHost):

    def __init__(self):
        self.path = LocalWindowsHostPath()
        self.sep = u"\\"

    def open(self, path, mode):
        # Just return a dummy file object.
        return StringIO.StringIO(u"")

    def walk(self, root):
        """
        Return a list of tuples as `os.walk`, but use tuples as if the
        directory structure was

        <root>
            dir1
                dir11
                file1
                file2

        where <root> is the string passed in as `root`.
        """
        join = ntpath.join
        return [(root,
                 [join(root, u"dir1")],
                 []),
                (join(root, u"dir1"),
                 [u"dir11"],
                 [u"file1", u"file2"])
                ]


class DummyFTPSession(object):

    def pwd(self):
        return u"/"

    def dir(self, *args):
        # Called by `_check_list_a_option`, otherwise not used.
        pass


class DummyFTPPath(object):

    def abspath(self, path):
        # Don't care here if the path is absolute or not.
        return path

    def isdir(self, path):
        return path[:-1].endswith(u"dir")

    def isfile(self, path):
        return path[:-1].endswith(u"file")


class ArgumentCheckingFTPHost(ftputil.FTPHost):

    def __init__(self, *args, **kwargs):
        super(ArgumentCheckingFTPHost, self).__init__(*args, **kwargs)
        self.path = DummyFTPPath()

    def _make_session(self, *args, **kwargs):
        return DummyFTPSession()

    def mkdir(self, path):
        assert u"\\" not in path

    def open(self, path, mode):
        assert u"\\" not in path
        return StringIO.StringIO(u"")


class TestUploadFromWindows(unittest.TestCase):

    def test_no_mixed_separators(self):
        source = LocalWindowsHost()
        target = ArgumentCheckingFTPHost()
        local_root = ntpath.join(u"some", u"directory")
        syncer = ftp_sync.Syncer(source, target)
        # If the following call raises any `AssertionError`s, the
        # `unittest` framework will catch them and show them.
        syncer.sync(local_root, u"not_used_by_ArgumentCheckingFTPHost")


if __name__ == '__main__':
    unittest.main()
