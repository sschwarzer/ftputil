# Copyright (C) 2002-2021, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import datetime
import errno
import ftplib
import io
import itertools
import os
import pickle
import posixpath
import random
import time
import unittest
import unittest.mock
import warnings

import pytest

import ftputil
import ftputil.error
import ftputil.file
import ftputil.path_encoding
import ftputil.tool
import ftputil.stat

from test import test_base
import test.scripted_session as scripted_session


Call = scripted_session.Call


#
# Helper function to generate random data
#
def binary_data():
    """
    Return a bytes object of length 10000, consisting of bytes from a pool of
    integer numbers in the range 0..255.
    """
    pool = list(range(0, 256))
    size = 10000
    integer_list = [random.choice(pool) for i in range(size)]
    return bytes(integer_list)


def as_bytes(string, encoding=ftputil.path_encoding.DEFAULT_ENCODING):
    return string.encode(encoding)


#
# Test cases
#

# For Python < 3.9, the `default_session_factory` is just `ftplib.FTP`. It's
# not worth it to test the factory then.
@pytest.mark.skipif(
    not ftputil.path_encoding.RUNNING_UNDER_PY39_AND_UP,
    reason="tests apply only to Python 3.9 and up",
)
class TestDefaultSessionFactory:
    def test_ftplib_FTP_subclass(self):
        """
        Test if the default factory is a subclass of `ftplib.FTP`.
        """
        assert issubclass(ftputil.host.default_session_factory, ftplib.FTP)

    def _test_extra_arguments(self, args=None, kwargs=None, expected_kwargs=None):
        """
        Test if `ftputil.FTPHost` accepts additional positional and keyword
        arguments, which are then passed to the session factory.
        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        if expected_kwargs is None:
            expected_kwargs = kwargs
        # Since our test server listens on a non-default port, we can't use the
        # session factory directly. We have to mock `ftplib.FTP` which is used
        # by ftputil's `default_session_factory`.
        with unittest.mock.patch("ftplib.FTP.__init__") as ftp_mock:
            # Prevent `TypeError` when Python checks the `__init__` result.
            ftp_mock.return_value = None
            session = ftputil.host.default_session_factory(
                "localhost", "ftptest", "dummy", *args, **kwargs
            )
            assert len(ftp_mock.call_args_list) == 1
            assert (
                # Don't compare the `self` argument. It changes for every test
                # run.
                ftp_mock.call_args.args
                == ("localhost", "ftptest", "dummy") + args
            )
            assert ftp_mock.call_args.kwargs == expected_kwargs

    def test_extra_positional_arguments(self):
        """
        Test if extra positional arguments are passed to the `ftplib.FTP`
        constructor.
        """
        expected_kwargs = {"encoding": ftputil.path_encoding.DEFAULT_ENCODING}
        # `acct`, `timeout`
        self._test_extra_arguments(
            args=("", 1.0), kwargs={}, expected_kwargs=expected_kwargs
        )

    def test_extra_keyword_arguments(self):
        """
        Test if extra keyword arguments are passed to the `ftplib.FTP`
        constructor.
        """
        kwargs = {"timeout": 1.0, "source_address": None}
        expected_kwargs = kwargs.copy()
        expected_kwargs["encoding"] = ftputil.path_encoding.DEFAULT_ENCODING
        self._test_extra_arguments(kwargs=kwargs, expected_kwargs=expected_kwargs)

    def test_custom_encoding(self):
        """
        Test if a custom encoding is passed to the base class constructor when
        running under Python 3.9 and up.
        """
        kwargs = {"timeout": 1.0, "source_address": None, "encoding": "latin-2"}
        self._test_extra_arguments(kwargs=kwargs)


class TestConstructor:
    """
    Test initialization of `FTPHost` objects.
    """

    def test_open_and_close(self):
        """
        Test if opening and closing an `FTPHost` object works as expected.
        """
        script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        host = test_base.ftp_host_factory(scripted_session.factory(script))
        host.close()
        assert host.closed is True
        assert host._children == []

    def test_invalid_login(self):
        """
        Login to invalid host must fail.
        """
        script = [Call("__init__", result=ftplib.error_perm), Call("pwd", result="/")]
        with pytest.raises(ftputil.error.FTPOSError):
            test_base.ftp_host_factory(scripted_session.factory(script))

    def test_pwd_normalization(self):
        """
        Test if the stored current directory is normalized.
        """
        script = [
            Call("__init__"),
            # Deliberately return the current working directory with a trailing
            # slash to test if it's removed when stored in the `FTPHost`
            # instance.
            Call("pwd", result="/home/"),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            assert host.getcwd() == "/home"

    def test_missing_encoding_attribute(self):
        """
        Test if a missing `encoding` attribute on the session instance leads to
        a `NoEncodingError`.
        """

        class InvalidSessionError:
            pass

        with pytest.raises(ftputil.error.NoEncodingError):
            _ = ftputil.host.FTPHost(session_factory=InvalidSessionError)


class TestKeepAlive:
    def test_succeeding_keep_alive(self):
        """
        Assume the connection is still alive.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `pwd` due to `keep_alive` call.
            Call("pwd", result="/"),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.keep_alive()

    def test_failing_keep_alive(self):
        """
        Assume the connection has timed out, so `keep_alive` fails.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/home"),
            # Simulate failing `pwd` call after the server closed the
            # connection due to a session timeout.
            Call("pwd", result=ftplib.error_temp),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with pytest.raises(ftputil.error.TemporaryError):
                host.keep_alive()


class TestSetParser:
    class TrivialParser(ftputil.stat.Parser):
        """
        An instance of this parser always returns the same result from its
        `parse_line` method. This is all we need to check if ftputil uses the
        set parser. No actual parsing code is required here.
        """

        def __init__(self):
            # We can't use `os.stat("/home")` directly because we later need
            # the object's `_st_name` attribute, which we can't set on a
            # `os.stat` stat value.
            default_stat_result = ftputil.stat.StatResult(os.stat("/home"))
            default_stat_result._st_name = "home"
            self.default_stat_result = default_stat_result

        def parse_line(self, line, time_shift=0.0):
            return self.default_stat_result

    def test_set_parser(self):
        """
        Test if the selected parser is used.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                result="drwxr-xr-x   2 45854    200           512 May  4  2000 home",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            assert host._stat._allow_parser_switching is True
            trivial_parser = TestSetParser.TrivialParser()
            host.set_parser(trivial_parser)
            stat_result = host.stat("/home")
            assert stat_result == trivial_parser.default_stat_result
            assert host._stat._allow_parser_switching is False


class TestCommandNotImplementedError:
    def test_command_not_implemented_error(self):
        """
        Test if we get the anticipated exception if a command isn't implemented
        by the server.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # `FTPHost.chmod` only raises a `CommandNotImplementedError` when
            # the exception text of the `ftplib.error_perm` starts with "502".
            Call(
                "voidcmd",
                result=ftplib.error_perm("502 command not implemented"),
                args=("SITE CHMOD 0644 nonexistent",),
            ),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # `FTPHost.chmod` only raises a `CommandNotImplementedError` when
            # the exception text of the `ftplib.error_perm` starts with "502".
            Call(
                "voidcmd",
                result=ftplib.error_perm("502 command not implemented"),
                args=("SITE CHMOD 0644 nonexistent",),
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with pytest.raises(ftputil.error.CommandNotImplementedError):
                host.chmod("nonexistent", 0o644)
            # `CommandNotImplementedError` is a subclass of `PermanentError`.
            with pytest.raises(ftputil.error.PermanentError):
                host.chmod("nonexistent", 0o644)


class TestRecursiveListingForDotAsPath:
    """
    These tests are for issue #33, see
    http://ftputil.sschwarzer.net/trac/ticket/33 .
    """

    def test_plain_listing(self):
        """
        If an empty string is passed to `FTPHost._dir` it should be passed to
        `session.dir` unmodified.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=(".",)),
            # Check that the empty string is passed on to `session.dir`.
            Call("dir", args=("",), result="non-recursive listing"),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            lines = host._dir(host.curdir)
            assert lines[0] == "non-recursive listing"

    def test_empty_string_instead_of_dot_workaround(self):
        """
        If `FTPHost.listdir` is called with a dot as argument, the underlying
        `session.dir` should _not_ be called with the dot as argument, but with
        an empty string.
        """
        dir_result = (
            "total 10\n"
            "lrwxrwxrwx   1 staff     7 Aug 13  2003 bin -> usr/bin\n"
            "d--x--x--x   2 staff   512 Sep 24  2000 dev\n"
            "d--x--x--x   3 staff   512 Sep 25  2000 etc\n"
            "dr-xr-xr-x   3 staff   512 Oct  3  2000 pub\n"
            "d--x--x--x   5 staff   512 Oct  3  2000 usr\n"
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_result),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            files = host.listdir(host.curdir)
            assert files == ["bin", "dev", "etc", "pub", "usr"]


class TestTimeShift:

    # Helper mock class that frees us from setting up complicated session
    # scripts for the remote calls.
    class _Path:
        def split(self, path):
            return posixpath.split(path)

        def set_mtime(self, mtime):
            self._mtime = mtime

        def getmtime(self, file_name):
            return self._mtime

        def join(self, *args):
            return posixpath.join(*args)

        def normpath(self, path):
            return posixpath.normpath(path)

        def isabs(self, path):
            return posixpath.isabs(path)

        def abspath(self, path):
            return "/_ftputil_sync_"

        # Needed for `isdir` in `FTPHost.remove`
        def isfile(self, path):
            return True

    def test_rounded_time_shift(self):
        """
        Test if time shift is rounded correctly.
        """
        script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        multisession_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            # Use private bound method.
            rounded_time_shift = host._FTPHost__rounded_time_shift
            # Pairs consisting of original value and expected result
            test_data = [
                (0, 0),
                (0.1, 0),
                (-0.1, 0),
                (1500, 1800),
                (-1500, -1800),
                (1800, 1800),
                (-1800, -1800),
                (2000, 1800),
                (-2000, -1800),
                (5 * 3600 - 100, 5 * 3600),
                (-5 * 3600 + 100, -5 * 3600),
            ]
            for time_shift, expected_time_shift in test_data:
                calculated_time_shift = rounded_time_shift(time_shift)
                assert calculated_time_shift == expected_time_shift

    def test_assert_valid_time_shift(self):
        """
        Test time shift sanity checks.
        """
        script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        multisession_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            # Use private bound method.
            assert_time_shift = host._FTPHost__assert_valid_time_shift
            # Valid time shifts
            test_data = [23 * 3600, -23 * 3600, 3600 + 30, -3600 + 30]
            for time_shift in test_data:
                assert assert_time_shift(time_shift) is None
            # Invalid time shift (exceeds one day)
            with pytest.raises(ftputil.error.TimeShiftError):
                assert_time_shift(25 * 3600)
            with pytest.raises(ftputil.error.TimeShiftError):
                assert_time_shift(-25 * 3600)
            # Invalid time shift (too large deviation from 15-minute units is
            # unacceptable)
            with pytest.raises(ftputil.error.TimeShiftError):
                assert_time_shift(8 * 60)
            with pytest.raises(ftputil.error.TimeShiftError):
                assert_time_shift(-3600 - 8 * 60)

    def test_synchronize_times(self):
        """
        Test time synchronization with server.
        """
        host_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("delete", args=("_ftputil_sync_",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd", args=("STOR _ftputil_sync_", None), result=io.BytesIO()
            ),
            Call("voidresp"),
            Call("close"),
        ]
        # Valid time shifts
        test_data = [
            (60 * 60 + 30, 60 * 60),
            (60 * 60 - 100, 60 * 60),
            (30 * 60 + 100, 30 * 60),
            (45 * 60 - 100, 45 * 60),
        ]
        for measured_time_shift, expected_time_shift in test_data:
            # Use a new `BytesIO` object to avoid exception
            # `ValueError: I/O operation on closed file`.
            file_script[4] = Call(
                "transfercmd", result=io.BytesIO(), args=("STOR _ftputil_sync_", None)
            )
            multisession_factory = scripted_session.factory(host_script, file_script)
            with test_base.ftp_host_factory(multisession_factory) as host:
                host.path = self._Path()
                host.path.set_mtime(time.time() + measured_time_shift)
                host.synchronize_times()
                assert host.time_shift() == expected_time_shift
        # Invalid time shifts
        measured_time_shifts = [60 * 60 + 8 * 60, 45 * 60 - 6 * 60]
        for measured_time_shift in measured_time_shifts:
            # Use a new `BytesIO` object to avoid exception
            # `ValueError: I/O operation on closed file`.
            file_script[4] = Call(
                "transfercmd", result=io.BytesIO(), args=("STOR _ftputil_sync_", None)
            )
            multisession_factory = scripted_session.factory(host_script, file_script)
            with test_base.ftp_host_factory(multisession_factory) as host:
                host.path = self._Path()
                host.path.set_mtime(time.time() + measured_time_shift)
                with pytest.raises(ftputil.error.TimeShiftError):
                    host.synchronize_times()

    def test_synchronize_times_for_server_in_east(self):
        """
        Test for timestamp correction (see ticket #55).
        """
        host_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("delete", args=("_ftputil_sync_",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd", args=("STOR _ftputil_sync_", None), result=io.BytesIO()
            ),
            Call("voidresp", args=()),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(session_factory=multisession_factory) as host:
            host.path = self._Path()
            # Set this explicitly to emphasize the problem.
            host.set_time_shift(0.0)
            hour = 60 * 60
            # This could be any negative time shift.
            presumed_time_shift = -6 * hour
            # Set `mtime` to simulate a server east of us.
            # In case the `time_shift` value for this host instance is 0.0
            # (as is to be expected before the time shift is determined), the
            # directory parser (more specifically
            # `ftputil.stat.Parser.parse_unix_time`) will return a time which
            # is a year too far in the past. The `synchronize_times` method
            # needs to deal with this and add the year "back". I don't think
            # this is a bug in `parse_unix_time` because the method should work
            # once the time shift is set correctly.
            client_time = datetime.datetime.now(datetime.timezone.utc)
            presumed_server_time = client_time.replace(
                year=client_time.year - 1
            ) + datetime.timedelta(seconds=presumed_time_shift)
            host.path.set_mtime(presumed_server_time.timestamp())
            host.synchronize_times()
            assert host.time_shift() == presumed_time_shift


class TestUploadAndDownload:
    """
    Test upload and download.
    """

    def test_download(self, tmp_path):
        """
        Test mode download.
        """
        remote_file_name = "dummy_name"
        remote_file_content = b"dummy_content"
        local_target = tmp_path / "test_target"
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("RETR {}".format(remote_file_name), None),
                result=io.BytesIO(remote_file_content),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        # Download
        with test_base.ftp_host_factory(multisession_factory) as host:
            host.download(remote_file_name, str(local_target))
        # Verify expected operations on mock socket as done in `FTPFile.close`.
        # We expect one `gettimeout` and two `settimeout` calls.
        file_session = multisession_factory.scripted_sessions[1]
        file_session.sock.gettimeout.assert_called_once_with()
        assert len(file_session.sock.settimeout.call_args_list) == 2
        assert file_session.sock.settimeout.call_args_list[0] == (
            (ftputil.file.FTPFile._close_timeout,),
            {},
        )
        assert file_session.sock.settimeout.call_args_list[1] == (
            (file_session.sock.gettimeout(),),
            {},
        )
        assert local_target.read_bytes() == remote_file_content

    def test_conditional_upload_without_upload(self, tmp_path):
        """
        If the target file is newer, no upload should happen.
        """
        local_source = tmp_path / "test_source"
        data = binary_data()
        local_source.write_bytes(data)
        dir_result = test_base.dir_line(
            mode_string="-rw-r--r--",
            date_=datetime.date.today() + datetime.timedelta(days=1),
            name="newer",
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_result),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        # Target is newer, so don't upload.
        #
        # This not only tests the return value, but also if a transfer
        # happened. If an upload was tried, our test framework would complain
        # about a missing scripted session for the `FTPFile` host.
        multisession_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            flag = host.upload_if_newer(str(local_source), "/newer")
        assert flag is False

    def test_conditional_upload_with_upload(self, tmp_path):
        """
        If the target file is older or doesn't exist, the source file should be
        uploaded.
        """
        local_source = tmp_path / "test_source"
        file_content = b"dummy_content"
        local_source.write_bytes(file_content)
        remote_file_name = "dummy_name"
        dir_result = test_base.dir_line(
            mode_string="-rw-r--r--",
            date_=datetime.date.today() - datetime.timedelta(days=1),
            name="older",
        )
        host_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_result),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("STOR older", None),
                result=test_base.MockableBytesIO(),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        # Target is older, so upload.
        multisession_factory = scripted_session.factory(host_script, file_script)
        with unittest.mock.patch("test.test_base.MockableBytesIO.write") as write_mock:
            with test_base.ftp_host_factory(multisession_factory) as host:
                flag = host.upload_if_newer(str(local_source), "/older")
            write_mock.assert_called_with(file_content)
        assert flag is True
        # Target doesn't exist, so upload.
        #  Use correct file name for this test.
        file_script[4] = Call(
            "transfercmd",
            args=("STOR notthere", None),
            result=test_base.MockableBytesIO(),
        )
        multisession_factory = scripted_session.factory(host_script, file_script)
        with unittest.mock.patch("test.test_base.MockableBytesIO.write") as write_mock:
            with test_base.ftp_host_factory(multisession_factory) as host:
                flag = host.upload_if_newer(str(local_source), "/notthere")
            write_mock.assert_called_with(file_content)
        assert flag is True

    def test_conditional_download_without_target(self, tmp_path):
        """
        Test conditional binary mode download when no target file exists.
        """
        local_target = tmp_path / "test_target"
        data = binary_data()
        # Target does not exist, so download.
        #  There isn't a `dir` call to compare the datetimes of the remote and
        #  the target file because the local `exists` call for the local target
        #  returns `False` and the datetime comparison therefore isn't done.
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("RETR newer", None), result=io.BytesIO(data)),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            flag = host.download_if_newer("/newer", str(local_target))
        assert flag is True
        assert local_target.read_bytes() == data

    def test_conditional_download_with_older_target(self, tmp_path):
        """
        Test conditional binary mode download with newer source file.
        """
        local_target = tmp_path / "test_target"
        # Make sure file exists for the timestamp comparison.
        local_target.touch()
        data = binary_data()
        # Target is older, so download.
        #  Use a date in the future. That isn't realistic, but for the purpose
        #  of the test it's an easy way to make sure the source file is newer
        #  than the target file.
        dir_result = test_base.dir_line(
            mode_string="-rw-r--r--",
            date_=datetime.date.today() + datetime.timedelta(days=1),
            name="newer",
        )
        host_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_result),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("RETR newer", None), result=io.BytesIO(data)),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            flag = host.download_if_newer("/newer", str(local_target))
        assert flag is True
        assert local_target.read_bytes() == data

    def test_conditional_download_with_newer_target(self, tmp_path):
        """
        Test conditional binary mode download with older source file.
        """
        local_target = tmp_path / "test_target"
        # Make sure file exists for timestamp comparison.
        local_target.touch()
        data = binary_data()
        # Use date in the past, so the target file is newer and no download
        # happens.
        dir_result = test_base.dir_line(
            mode_string="-rw-r--r--",
            date_=datetime.date.today() - datetime.timedelta(days=1),
            name="newer",
        )
        host_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_result),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("RETR newer", None), result=io.BytesIO(data)),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            flag = host.download_if_newer("/newer", str(local_target))
        assert flag is False


class TestMakedirs:
    def test_exist_ok_false(self):
        """
        If `exist_ok` is `False` or not specified, an existing leaf directory
        should lead to a `PermanentError` with `errno` set to 17.
        """
        # No `exist_ok` specified
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/part1",)),
            Call("cwd", args=("/part1/part2",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory=multisession_factory) as host:
            with pytest.raises(ftputil.error.PermanentError) as exc_info:
                host.makedirs("/part1/part2")
            assert isinstance(exc_info.value, ftputil.error.PermanentError)
            assert exc_info.value.errno == errno.EEXIST
        # `exist_ok` explicitly set to `False`
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/part1",)),
            Call("cwd", args=("/part1/part2",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory=multisession_factory) as host:
            with pytest.raises(ftputil.error.PermanentError) as exc_info:
                host.makedirs("/part1/part2", exist_ok=False)
            assert isinstance(exc_info.value, ftputil.error.PermanentError)
            assert exc_info.value.errno == errno.EEXIST

    def test_exist_ok_true(self):
        """
        If `exist_ok` is `True`, an existing leaf directory should _not_ lead
        to an exception.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/part1",)),
            Call("cwd", args=("/part1/part2",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory=multisession_factory) as host:
            host.makedirs("/part1/part2", exist_ok=True)


class TestAcceptEitherUnicodeOrBytes:
    """
    Test whether certain `FTPHost` methods accept either unicode
    or byte strings for the path(s).
    """

    def test_upload(self):
        """
        Test whether `upload` accepts either unicode or bytes.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("STOR target", None), result=io.BytesIO()),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        # The source file needs to be present in the current directory.
        with test_base.ftp_host_factory(multisession_factory) as host:
            host.upload("Makefile", "target")
        # Create new `BytesIO` object.
        file_script[4] = Call(
            "transfercmd", args=("STOR target", None), result=io.BytesIO()
        )
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            host.upload("Makefile", as_bytes("target"))

    def test_download(self, tmp_path):
        """
        Test whether `download` accepts either unicode or bytes.
        """
        local_target = tmp_path / "local_target"
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("RETR source", None), result=io.BytesIO()),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        # The source file needs to be present in the current directory.
        with test_base.ftp_host_factory(multisession_factory) as host:
            host.download("source", str(local_target))
        # Create new `BytesIO` object.
        file_script[4] = Call(
            "transfercmd", args=("RETR source", None), result=io.BytesIO()
        )
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            host.download(as_bytes("source"), str(local_target))

    def test_rename(self):
        """
        Test whether `rename` accepts either unicode or bytes.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("rename", args=("/ä", "/ä")),
            Call("close"),
        ]
        # It's possible to mix argument types, as for `os.rename`.
        path_as_str = "/ä"
        path_as_bytes = as_bytes(
            path_as_str, ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING
        )
        paths = [path_as_str, path_as_bytes]
        for source_path, target_path in itertools.product(paths, paths):
            # Uses ftplib default encoding
            session_factory = scripted_session.factory(script)
            with test_base.ftp_host_factory(session_factory) as host:
                host.rename(source_path, target_path)

    def test_listdir(self):
        """
        Test whether `listdir` accepts either unicode or bytes.
        """
        top_level_dir_line = test_base.dir_line(
            mode_string="drwxr-xr-x", date_=datetime.date.today(), name="ä"
        )
        dir_line1 = test_base.dir_line(
            mode_string="-rw-r--r--", date_=datetime.date.today(), name="ö"
        )
        dir_line2 = test_base.dir_line(
            mode_string="-rw-r--r--", date_=datetime.date.today(), name="o"
        )
        dir_result = dir_line1 + "\n" + dir_line2
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=top_level_dir_line),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/ä",)),
            Call("dir", args=("",), result=dir_result),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        # Unicode
        session_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory) as host:
            items = host.listdir("ä")
        assert items == ["ö", "o"]
        # Bytes
        session_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory) as host:
            items = host.listdir(
                as_bytes("ä", ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING)
            )
            assert items == [
                as_bytes("ö", ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING),
                as_bytes("o"),
            ]

    def test_chmod(self):
        """
        Test whether `chmod` accepts either unicode or bytes.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("SITE CHMOD 0755 ä",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        path = "/ä"
        # Unicode
        session_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory) as host:
            host.chmod(path, 0o755)
        # Bytes
        session_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory) as host:
            host.chmod(
                as_bytes(path, ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING), 0o755
            )

    def _test_method_with_single_path_argument(self, method_name, path, script):
        # Unicode
        session_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory) as host:
            method = getattr(host, method_name)
            method(path)
        # Bytes
        session_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory) as host:
            method = getattr(host, method_name)
            method(as_bytes(path, ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING))

    def test_chdir(self):
        """
        Test whether `chdir` accepts either unicode or bytes.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/ö",)),
            Call("close"),
        ]
        self._test_method_with_single_path_argument("chdir", "/ö", script)

    def test_mkdir(self):
        """
        Test whether `mkdir` accepts either unicode or bytes.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("mkd", args=("ä",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        self._test_method_with_single_path_argument("mkdir", "/ä", script)

    def test_makedirs(self):
        """
        Test whether `makedirs` accepts either unicode or bytes.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # To deal with ticket #86 (virtual directories), `makedirs` tries
            # to change into each directory and if it exists (changing doesn't
            # raise an exception), doesn't try to create it. That's why you
            # don't see an `mkd` calls here despite originally having a
            # `makedirs` call.
            Call("cwd", args=("/ä",)),
            # If `exist_ok` is `False` (which is the default), the leaf
            # directory to make must not exist. In other words, the `chdir`
            # call is `makedirs` must fail with a permanent error.
            Call("cwd", args=("/ä/ö",), result=ftplib.error_perm),
            Call("cwd", args=("/ä",)),
            Call("cwd", args=("/ä",)),
            Call("mkd", args=("ö",)),
            # From `isdir` call
            Call("cwd", args=("/ä",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        self._test_method_with_single_path_argument("makedirs", "/ä/ö", script)

    def test_rmdir(self):
        """
        Test whether `rmdir` accepts either unicode or bytes.
        """
        dir_line = test_base.dir_line(
            mode_string="drwxr-xr-x", date_=datetime.date.today(), name="empty_ä"
        )
        # Since the session script isn't at all obvious, I checked it with a
        # debugger and added comments on some of the calls that happen during
        # the `rmdir` call.
        #
        # `_robust_ftp_command` descends one directory at a time (see ticket
        # #11) and restores the original directory in the end, which results in
        # at least four calls on the FTP session object (`cwd`, `cwd`, actual
        # method, `cwd`). It would be great if all the roundtrips to the server
        # could be reduced.
        script = [
            # `FTPHost` initialization
            Call("__init__"),
            Call("pwd", result="/"),
            # `host.rmdir("/empty_ä")`
            #  `host.listdir("/empty_ä")`
            #   `host._stat._listdir("/empty_ä")`
            #    `host._stat.__call_with_parser_retry("/empty_ä")`
            #     `host._stat._real_listdir("/empty_ä")`
            #      `host.path.isdir("/empty_ä")`
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            #      `host.path.isdir` end
            #      `host._stat._stat_results_from_dir("/empty_ä")`
            Call("cwd", args=("/",)),
            Call("cwd", args=("/empty_ä",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            #      `host._stat._stat_results_from_dir("/empty_ä")` end
            #  `host._session.rmd` in `host._robust_ftp_command`
            #   `host._check_inaccessible_login_directory()`
            Call("cwd", args=("/",)),
            #   `host.chdir(head)` ("/")
            Call("cwd", args=("/",)),
            #   `host.rmd(tail)` ("empty_ä")
            Call("rmd", args=("empty_ä",)),
            #   `host.chdir(old_dir)` ("/")
            Call("cwd", args=("/",)),
            #
            Call("close"),
        ]
        empty_directory_as_required_by_rmdir = "/empty_ä"
        self._test_method_with_single_path_argument(
            "rmdir", empty_directory_as_required_by_rmdir, script
        )

    def test_remove(self):
        """
        Test whether `remove` accepts either unicode or bytes.
        """
        dir_line = test_base.dir_line(
            mode_string="-rw-r--r--", date_=datetime.date.today(), name="ö"
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("delete", args=("ö",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        self._test_method_with_single_path_argument("remove", "/ö", script)

    def test_rmtree(self):
        """
        Test whether `rmtree` accepts either unicode or bytes.
        """
        dir_line = test_base.dir_line(
            mode_string="drwxr-xr-x", date_=datetime.date.today(), name="empty_ä"
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # Recursive `listdir`
            #  Check parent (root) directory.
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/empty_ä",)),
            #  Child directory (inside `empty_ä`)
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/empty_ä",)),
            # Recursive `rmdir` (repeated `cwd` calls because of
            # `_robust_ftp_command`)
            Call("dir", result="", args=("",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("rmd", args=("empty_ä",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        empty_directory_as_required_by_rmtree = "/empty_ä"
        self._test_method_with_single_path_argument(
            "rmtree", empty_directory_as_required_by_rmtree, script
        )

    def test_lstat(self):
        """
        Test whether `lstat` accepts either unicode or bytes.
        """
        dir_line = test_base.dir_line(
            mode_string="-rw-r--r--", date_=datetime.date.today(), name="ä"
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        self._test_method_with_single_path_argument("lstat", "/ä", script)

    def test_stat(self):
        """
        Test whether `stat` accepts either unicode or bytes.
        """
        dir_line = test_base.dir_line(
            mode_string="-rw-r--r--", date_=datetime.date.today(), name="ä"
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        self._test_method_with_single_path_argument("stat", "/ä", script)

    def test_walk(self):
        """
        Test whether `walk` accepts either unicode or bytes.
        """
        dir_line = test_base.dir_line(
            mode_string="-rw-r--r--", date_=datetime.date.today(), name="ä"
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        # We're not interested in the return value of `walk`.
        # Unicode
        session_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory) as host:
            result = list(host.walk("/ä"))
        # Bytes
        session_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(session_factory) as host:
            result = list(
                host.walk(as_bytes("/ä", ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING))
            )


class TestFailingPickling:
    def test_failing_pickling(self):
        """
        Test if pickling (intentionally) isn't supported.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("RETR test", None), result=io.BytesIO()),
            Call("voidresp", args=()),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with pytest.raises(TypeError):
                pickle.dumps(host)
            with host.open("/test") as file_obj:
                with pytest.raises(TypeError):
                    pickle.dumps(file_obj)
