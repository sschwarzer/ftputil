# Copyright (C) 2002-2019, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import ftplib
import io
import unittest

import pytest

import ftputil.error

from test import scripted_session
from test import test_base


Call = scripted_session.Call


# Test data for use in text/binary read/write tests.
TEXT_TEST_DATA = " söme line\r\nänother line\n almost done\n"
BINARY_TEST_DATA = TEXT_TEST_DATA.encode("UTF-8")


class TestFileOperations:
    """Test operations with file-like objects."""

    def test_inaccessible_dir(self):
        """
        Test whether opening a file at an invalid location fails.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("STOR inaccessible", None),
                result=ftplib.error_perm,
            ),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with pytest.raises(ftputil.error.FTPIOError):
                host.open("/inaccessible", "w")

    def test_caching_of_children(self):
        """
        Test whether `FTPFile` cache of `FTPHost` object works.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file1_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("STOR path1", None), result=io.StringIO("")),
            Call("voidresp"),
            # Open a file again while reusing the child object and with it its
            # `_session` attribute (the `ftplib.FTP` object).
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("STOR path1", None), result=io.StringIO("")),
            Call("voidresp"),
            Call("close"),
        ]
        file2_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", result=io.StringIO(""), args=("STOR path2", None)),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(
            host_script, file1_script, file2_script
        )
        with test_base.ftp_host_factory(multisession_factory) as host:
            assert len(host._children) == 0
            path1 = "path1"
            path2 = "path2"
            # Open one file and inspect cache of available children.
            file1 = host.open(path1, "w")
            child1 = host._children[0]
            assert len(host._children) == 1
            assert not child1._file.closed
            # Open another file.
            file2 = host.open(path2, "w")
            child2 = host._children[1]
            assert len(host._children) == 2
            assert not child2._file.closed
            # Close first file.
            file1.close()
            assert len(host._children) == 2
            assert child1._file.closed
            assert not child2._file.closed
            # Re-open first child's file.
            file1 = host.open(path1, "w")
            child1_1 = file1._host
            # Check if it's reused.
            assert child1 is child1_1
            assert not child1._file.closed
            assert not child2._file.closed
            # Close second file.
            file2.close()
            assert child2._file.closed

    def test_write_to_directory(self):
        """
        Test whether attempting to write to a directory fails.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("STOR some_directory", None),
                result=ftplib.error_perm,
            ),
            # Because of the exception, `voidresp` isn't called.
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with pytest.raises(ftputil.error.FTPIOError):
                host.open("/some_directory", "w")

    def test_mode_not_given(self):
        """
        If the mode isn't given, a file should be opened in text read mode.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("RETR some_file", None),
                result=io.StringIO(TEXT_TEST_DATA),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with host.open("some_file") as fobj:
                data = fobj.read()
            assert data == TEXT_TEST_DATA

    def test_mode_is_none(self):
        """
        If the mode is passed as `None`, a `TypeError` should be raised.

        (This is Python's behavior for local files.)
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with pytest.raises(TypeError):
                with host.open("some_file", None) as fobj:
                    pass

    def test_binary_read(self):
        """
        Read data from a binary file.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("RETR some_file", None),
                result=io.BytesIO(BINARY_TEST_DATA),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with host.open("some_file", "rb") as fobj:
                data = fobj.read()
            assert data == BINARY_TEST_DATA

    def test_binary_write(self):
        """
        Write binary data with `write`.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("STOR some_file", None),
                result=test_base.MockableBytesIO(b""),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with unittest.mock.patch("test.test_base.MockableBytesIO.write") as write_mock:
            with test_base.ftp_host_factory(multisession_factory) as host:
                with host.open("some_file", "wb") as output:
                    output.write(BINARY_TEST_DATA)
            write_mock.assert_called_with(BINARY_TEST_DATA)

    def test_text_read(self):
        """
        Read text with plain `read`.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("RETR dummy", None),
                # Use the same `newline` as `host.open` call. The default for
                # `StringIO`'s `newline` differs from the default for `open`
                # and `socket.makefile`.
                result=io.StringIO(TEXT_TEST_DATA, newline=None),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with host.open("dummy", "r") as input_:
                data = input_.read(0)
                assert data == ""
                data = input_.read(3)
                assert data == " sö"
                # Specifically check the behavior around the line ending
                # character.
                data = input_.read(7)
                assert data == "me line"
                data = input_.read(1)
                assert data == "\n"
                data = input_.read()
                assert data == "änother line\n almost done\n"
                data = input_.read()
                assert data == ""

    def test_text_write(self):
        """
        Write text with `write`.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("STOR dummy", None),
                # Use the same `newline` as `host.open` call. The default for
                # `StringIO`'s `newline` differs from the default for `open`
                # and `socket.makefile`.
                result=test_base.MockableStringIO(newline="\r\n"),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with unittest.mock.patch("test.test_base.MockableStringIO.write") as write_mock:
            with test_base.ftp_host_factory(multisession_factory) as host:
                with host.open("dummy", "w", newline="\r\n") as output:
                    output.write(TEXT_TEST_DATA)
        write_mock.assert_called_with(TEXT_TEST_DATA)

    def test_text_writelines(self):
        """
        Write text with `writelines`.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("STOR dummy", None),
                # Use the same `newline` as `host.open` call. The default for
                # `StringIO`'s `newline` differs from the default for `open`
                # and `socket.makefile`.
                result=test_base.MockableStringIO(newline="\r\n"),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        data = [" söme line\r\n", "änother line\n", " almost done\n"]
        print("=== data:", data)
        backup_data = data[:]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with unittest.mock.patch(
            "test.test_base.MockableStringIO.writelines"
        ) as write_mock:
            with test_base.ftp_host_factory(multisession_factory) as host:
                with host.open("dummy", "w", newline="\r\n") as output:
                    output.writelines(data)
        write_mock.assert_called_with(data)
        # Ensure that the original data was not modified.
        assert data == backup_data

    def test_binary_readline(self):
        """
        Read binary data with `readline`.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("RETR dummy", None),
                result=io.BytesIO(BINARY_TEST_DATA),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with host.open("dummy", "rb") as input_:
                data = input_.readline(3)
                assert data == b" s\xc3"
                data = input_.readline(9)
                assert data == b"\xb6me line\r"
                # 30 = at most 30 bytes
                data = input_.readline(30)
                assert data == b"\n"
                data = input_.readline()
                assert data == b"\xc3\xa4nother line\n"
                data = input_.readline()
                assert data == b" almost done\n"
                data = input_.readline()
                assert data == b""

    def test_text_readline(self):
        """
        Read text with `readline`.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("RETR dummy", None),
                # Use the same `newline` as `host.open` call. The default for
                # `StringIO`'s `newline` differs from the default for `open`
                # and `socket.makefile`.
                result=io.StringIO(TEXT_TEST_DATA, newline=None),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with host.open("dummy", "r") as input_:
                data = input_.readline(3)
                assert data == " sö"
                data = input_.readline(7)
                assert data == "me line"
                data = input_.readline(10)
                # Does implicit newline conversion.
                assert data == "\n"
                # 30 = at most 30 bytes
                data = input_.readline(30)
                assert data == "änother line\n"
                data = input_.readline()
                assert data == " almost done\n"
                data = input_.readline()
                assert data == ""

    def test_text_readlines(self):
        """
        Read text with `readlines`.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("RETR dummy", None),
                # Use the same `newline` as `host.open` call. The default for
                # `StringIO`'s `newline` differs from the default for `open`
                # and `socket.makefile`.
                result=io.StringIO(TEXT_TEST_DATA, newline=None),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with host.open("dummy", "r") as input_:
                data = input_.read(3)
                assert data == " sö"
                data = input_.readlines()
                assert data == ["me line\n", "änother line\n", " almost done\n"]
                input_.close()

    def test_binary_iterator(self):
        """
        Test iterator interface of `FTPFile` objects for binary files.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("RETR dummy", None),
                result=io.BytesIO(BINARY_TEST_DATA),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with host.open("dummy", "rb") as input_:
                input_iterator = iter(input_)
                assert next(input_iterator) == b" s\xc3\xb6me line\r\n"
                # The last two lines don't have a `\r`.
                assert next(input_iterator) == b"\xc3\xa4nother line\n"
                assert next(input_iterator) == b" almost done\n"
                with pytest.raises(StopIteration):
                    input_iterator.__next__()

    def test_text_iterator(self):
        """
        Test iterator interface of `FTPFile` objects for text files.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("RETR dummy", None),
                # Use the same `newline` as `host.open` call. The default for
                # `StringIO`'s `newline` differs from the default for `open`
                # and `socket.makefile`.
                result=io.StringIO(TEXT_TEST_DATA, newline=None),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with host.open("dummy", "r") as input_:
                input_iterator = iter(input_)
                assert next(input_iterator) == " söme line\n"
                assert next(input_iterator) == "änother line\n"
                assert next(input_iterator) == " almost done\n"
                with pytest.raises(StopIteration):
                    input_iterator.__next__()

    def test_read_unknown_file(self):
        """
        Test whether reading a file which isn't there fails.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("RETR notthere", None), result=ftplib.error_perm),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with pytest.raises(ftputil.error.FTPIOError):
                with host.open("notthere", "r") as input_:
                    pass


class TestAvailableChild:
    def _failing_pwd(self, exception_class):
        """
        Return a function that will be used instead of the `session.pwd` and
        will raise the exception `exception_to_raise`.
        """

        def new_pwd():
            raise exception_class("")

        return new_pwd

    def _test_with_pwd_error(self, exception_class):
        """
        Test if reusing a child session fails because of
        `child_host._session.pwd` raising an exception of type
        `exception_class`.
        """
        host_script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        first_file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("RETR dummy1", None), result=io.StringIO("")),
            Call("voidresp"),
            # This `pwd` is executed from `FTPHost._available_child`.
            Call("pwd", result=exception_class),
            Call("close"),
        ]
        second_file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("RETR dummy2", None), result=io.StringIO("")),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(
            host_script, first_file_script, second_file_script
        )
        with test_base.ftp_host_factory(multisession_factory) as host:
            # Implicitly create a child session.
            with host.open("/dummy1") as _:
                pass
            assert len(host._children) == 1
            # Try to create a new file. Since `pwd` in
            # `FTPHost._available_child` raises an exception, a new child
            # session should be created.
            with host.open("/dummy2") as _:
                pass
            assert len(host._children) == 2

    def test_pwd_with_error_temp(self):
        """
        Test if an `error_temp` in `_session.pwd` skips the child session.
        """
        self._test_with_pwd_error(ftplib.error_temp)

    def test_pwd_with_error_reply(self):
        """
        Test if an `error_reply` in `_session.pwd` skips the child session.
        """
        self._test_with_pwd_error(ftplib.error_reply)

    def test_pwd_with_OSError(self):
        """
        Test if an `OSError` in `_session.pwd` skips the child session.
        """
        self._test_with_pwd_error(OSError)

    def test_pwd_with_EOFError(self):
        """
        Test if an `EOFError` in `_session.pwd` skips the child session.
        """
        self._test_with_pwd_error(EOFError)
