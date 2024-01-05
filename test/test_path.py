# Copyright (C) 2003-2021, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import datetime
import ftplib
import functools
import time

import pytest

import ftputil
import ftputil.error
import ftputil.path_encoding
import ftputil.tool

from test import test_base
from test import scripted_session


Call = scripted_session.Call


def as_bytes(string, encoding=ftputil.path_encoding.DEFAULT_ENCODING):
    return string.encode(encoding)


class TestPath:
    """Test operations in `FTPHost.path`."""

    # TODO: Add unit tests for changes for ticket #113 (commits [b4c9b089b6b8]
    # and [4027740cdd2d]).
    def test_regular_isdir_isfile_islink(self):
        """
        Test regular `FTPHost._Path.isdir/isfile/islink`.
        """
        # Test a path which isn't there.
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `isdir` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            # `isfile` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            # `islink` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert not host.path.isdir("notthere")
            assert not host.path.isfile("notthere")
            assert not host.path.islink("notthere")
        # This checks additional code (see ticket #66).
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `isdir` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            # `isfile` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            # `islink` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert not host.path.isdir("/notthere/notthere")
            assert not host.path.isfile("/notthere/notthere")
            assert not host.path.islink("/notthere/notthere")
        # Test a directory.
        test_dir = "/some_dir"
        dir_line = test_base.dir_line(
            mode_string="dr-xr-xr-x",
            datetime_=datetime.datetime.now(),
            name=test_dir.lstrip("/"),
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `isdir` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            # `isfile` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            # `islink` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert host.path.isdir(test_dir)
            assert not host.path.isfile(test_dir)
            assert not host.path.islink(test_dir)
        # Test a file.
        test_file = "/some_file"
        dir_line = test_base.dir_line(
            datetime_=datetime.datetime.now(), name=test_file.lstrip("/")
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `isdir` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            # `isfile` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            # `islink` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert not host.path.isdir(test_file)
            assert host.path.isfile(test_file)
            assert not host.path.islink(test_file)
        # Test a link. Since the link target doesn't exist, neither
        # `isdir` nor `isfile` return `True`.
        test_link = "/some_link"
        dir_line = test_base.dir_line(
            mode_string="lrwxrwxrwx",
            datetime_=datetime.datetime.now(),
            name=test_link.lstrip("/"),
            link_target="nonexistent",
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `isdir` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            #  Look for `/some_link`
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            #  Look for `/nonexistent`
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            # `isfile` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            #  Look for `/some_link`
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            #  Look for `/nonexistent`
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            # `islink` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            #  Look for `/some_link`. `islink` doesn't try to dereference
            #  the link.
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert not host.path.isdir(test_link)
            assert not host.path.isfile(test_link)
            assert host.path.islink(test_link)

    def test_workaround_for_spaces(self):
        """
        Test whether the workaround for space-containing paths is used.
        """
        # Test a file name containing spaces.
        test_file = "/home/dir with spaces/file with spaces"
        dir_line1 = test_base.dir_line(
            mode_string="dr-xr-xr-x", datetime_=datetime.datetime.now(), name="home"
        )
        dir_line2 = test_base.dir_line(
            mode_string="dr-xr-xr-x",
            datetime_=datetime.datetime.now(),
            name="dir with spaces",
        )
        dir_line3 = test_base.dir_line(
            mode_string="-r--r--r--",
            datetime_=datetime.datetime.now(),
            name="file with spaces",
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `isdir` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line1),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/home",)),
            Call("dir", args=("",), result=dir_line2),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/home/dir with spaces",)),
            Call("dir", args=("",), result=dir_line3),
            Call("cwd", args=("/",)),
            # `isfile` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line1),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/home",)),
            Call("dir", args=("",), result=dir_line2),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/home/dir with spaces",)),
            Call("dir", args=("",), result=dir_line3),
            Call("cwd", args=("/",)),
            # `islink` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line1),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/home",)),
            Call("dir", args=("",), result=dir_line2),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/home/dir with spaces",)),
            Call("dir", args=("",), result=dir_line3),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert not host.path.isdir(test_file)
            assert host.path.isfile(test_file)
            assert not host.path.islink(test_file)

    def test_inaccessible_home_directory_and_whitespace_workaround(self):
        """
        Test combination of inaccessible home directory + whitespace in path.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", result=ftplib.error_perm),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with pytest.raises(ftputil.error.InaccessibleLoginDirError):
                host._dir("/home dir")

    def test_isdir_isfile_islink_with_dir_failure(self):
        """
        Test failing `FTPHost._Path.isdir/isfile/islink` because of failing
        `_dir` call.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=ftplib.error_perm),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        FTPOSError = ftputil.error.FTPOSError
        # Test if exceptions are propagated.
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with pytest.raises(FTPOSError):
                host.path.isdir("index.html")
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with pytest.raises(FTPOSError):
                host.path.isfile("index.html")
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with pytest.raises(FTPOSError):
                host.path.islink("index.html")

    def test_isdir_isfile_with_infinite_link_chain(self):
        """
        Test if `isdir` and `isfile` return `False` if they encounter an
        infinite link chain.
        """
        # `/home/bad_link` links to `/home/subdir/bad_link`, which links back
        # to `/home/bad_link` etc.
        dir_line1 = test_base.dir_line(
            mode_string="dr-xr-xr-x", datetime_=datetime.datetime.now(), name="home"
        )
        dir_line2 = test_base.dir_line(
            mode_string="lrwxrwxrwx",
            datetime_=datetime.datetime.now(),
            name="bad_link",
            link_target="subdir/bad_link",
        )
        dir_line3 = test_base.dir_line(
            mode_string="dr-xr-xr-x", datetime_=datetime.datetime.now(), name="subdir"
        )
        dir_line4 = test_base.dir_line(
            mode_string="lrwxrwxrwx",
            datetime_=datetime.datetime.now(),
            name="bad_link",
            link_target="/home/bad_link",
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line1),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/home",)),
            Call("dir", args=("",), result=dir_line2 + "\n" + dir_line3),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/home/subdir",)),
            Call("dir", args=("",), result=dir_line4),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            assert host.path.isdir("/home/bad_link") is False
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            assert host.path.isfile("/home/bad_link") is False

    def test_exists(self):
        """
        Test `FTPHost.path.exists`.
        """
        # Regular use of `exists`
        dir_line1 = test_base.dir_line(
            datetime_=datetime.datetime.now(), name="some_file"
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `exists("some_file")`
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line1),
            Call("cwd", args=("/",)),
            # `exists("notthere")`
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line1),
            Call("cwd", args=("/",)),
            # `exists` with failing `dir` call
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=ftplib.error_perm),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert host.path.exists("some_file")
            assert not host.path.exists("notthere")
            # Test if exceptions are propagated.
            with pytest.raises(ftputil.error.FTPOSError):
                host.path.exists("some_file")


class TestAcceptEitherBytesOrStr:

    # Use path arguments directly
    path_converter = staticmethod(lambda path: path)

    def _test_method_string_types(self, method, path):
        expected_type = type(path)
        path_converter = self.path_converter
        assert isinstance(method(path_converter(path)), expected_type)

    def test_methods_that_take_and_return_one_string(self):
        """
        Test whether the same string type as for the argument is returned.
        """
        method_names = [
            "abspath",
            "basename",
            "dirname",
            "join",
            "normcase",
            "normpath",
        ]
        script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            for method_name in method_names:
                method = getattr(host.path, method_name)
                self._test_method_string_types(method, "/")
                self._test_method_string_types(method, ".")
                self._test_method_string_types(method, b"/")
                self._test_method_string_types(method, b".")

    def test_methods_that_take_a_string_and_return_a_bool(self):
        """
        Test whether the methods accept byte and unicode strings.
        """
        path_converter = self.path_converter
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `exists` test 1
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(name="ä", datetime_=datetime.datetime.now()),
            ),
            Call("cwd", args=("/",)),
            # `exists` test 2
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(name="ä", datetime_=datetime.datetime.now()),
            ),
            Call("cwd", args=("/",)),
            # `isdir` test 1
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(
                    mode_string="dr-xr-xr-x",
                    name="ä",
                    datetime_=datetime.datetime.now(),
                ),
            ),
            Call("cwd", args=("/",)),
            # `isdir` test 2
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(
                    mode_string="dr-xr-xr-x",
                    name="ä",
                    datetime_=datetime.datetime.now(),
                ),
            ),
            Call("cwd", args=("/",)),
            # `isfile` test 1
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(name="ö", datetime_=datetime.datetime.now()),
            ),
            Call("cwd", args=("/",)),
            # `isfile` test 2
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(name="ö", datetime_=datetime.datetime.now()),
            ),
            Call("cwd", args=("/",)),
            # `islink` test 1
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(
                    mode_string="lrwxrwxrwx",
                    name="ü",
                    datetime_=datetime.datetime.now(),
                    link_target="unimportant",
                ),
            ),
            Call("cwd", args=("/",)),
            # `islink` test 2
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(
                    mode_string="lrwxrwxrwx",
                    name="ü",
                    datetime_=datetime.datetime.now(),
                    link_target="unimportant",
                ),
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        custom_as_bytes = functools.partial(
            as_bytes, encoding=ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING
        )
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            # `isabs`
            assert not host.path.isabs("ä")
            assert not host.path.isabs(path_converter(custom_as_bytes("ä")))
            # `exists`
            assert host.path.exists(path_converter("ä"))
            assert host.path.exists(path_converter(custom_as_bytes("ä")))
            # `isdir`, `isfile`, `islink`
            assert host.path.isdir(path_converter("ä"))
            assert host.path.isdir(path_converter(custom_as_bytes("ä")))
            assert host.path.isfile(path_converter("ö"))
            assert host.path.isfile(path_converter(custom_as_bytes("ö")))
            assert host.path.islink(path_converter("ü"))
            assert host.path.islink(path_converter(custom_as_bytes("ü")))

    def test_getmtime(self):
        """
        Test whether `FTPHost.path.getmtime` accepts byte and unicode paths.
        """
        path_converter = self.path_converter
        now = datetime.datetime.now(datetime.timezone.utc)
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `getmtime` call 1
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=test_base.dir_line(name="ä", datetime_=now)),
            Call("cwd", args=("/",)),
            # `getmtime` call 2
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=test_base.dir_line(name="ä", datetime_=now)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        expected_mtime = now.timestamp()
        # We don't care about the _exact_ time, so don't bother with timezone
        # differences. Instead, do a simple sanity check.
        day = 24 * 60 * 60  # seconds
        mtime_makes_sense = (
            lambda mtime: expected_mtime - day <= mtime <= expected_mtime + day
        )
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert mtime_makes_sense(host.path.getmtime(path_converter(("ä"))))
            assert mtime_makes_sense(
                host.path.getmtime(
                    path_converter(
                        as_bytes("ä", ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING)
                    )
                )
            )

    def test_getsize(self):
        """
        Test whether `FTPHost.path.getsize` accepts byte and unicode paths.
        """
        path_converter = self.path_converter
        now = datetime.datetime.now()
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `getsize` call 1
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(name="ä", size=512, datetime_=now),
            ),
            Call("cwd", args=("/",)),
            # `getsize` call 2
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(name="ä", size=512, datetime_=now),
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert host.path.getsize(path_converter("ä")) == 512
            assert (
                host.path.getsize(
                    path_converter(
                        as_bytes("ä", ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING)
                    )
                )
                == 512
            )

    def test_walk(self):
        """
        Test whether `FTPHost.path.walk` accepts bytes and unicode paths.
        """
        path_converter = self.path_converter
        now = datetime.datetime.now()
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `walk` call 1
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(
                    mode_string="dr-xr-xr-x", name="ä", size=512, datetime_=now
                ),
            ),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/ä",)),
            #  Assume directory `ä` is empty.
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            # `walk` call 2
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(
                    mode_string="dr-xr-xr-x", name="ä", size=512, datetime_=now
                ),
            ),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/ä",)),
            #  Assume directory `ä` is empty.
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            Call("close"),
        ]

        def noop(arg, top, names):
            del names[:]

        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            host.path.walk(path_converter("ä"), func=noop, arg=None)
            host.path.walk(
                path_converter(
                    as_bytes("ä", ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING)
                ),
                func=noop,
                arg=None,
            )


class Path:
    def __init__(self, path):
        self.path = path

    def __fspath__(self):
        return self.path


class TestAcceptEitherBytesOrStrFromPath(TestAcceptEitherBytesOrStr):

    # Take path arguments from `Path(...)` objects
    path_converter = Path
