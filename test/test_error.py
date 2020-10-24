# Copyright (C) 2002-2020, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import ftplib
import socket

import pytest

import ftputil.error


class TestFTPErrorArguments:
    """
    The `*Error` constructors should accept either a byte string or a unicode
    string.
    """

    def test_bytestring_argument(self):
        # An umlaut as latin-1 character
        io_error = ftputil.error.FTPIOError(b"\xe4")
        os_error = ftputil.error.FTPOSError(b"\xe4")

    def test_unicode_argument(self):
        # An umlaut as unicode character
        io_error = ftputil.error.FTPIOError("\xe4")
        os_error = ftputil.error.FTPOSError("\xe4")


class TestErrorConversion:
    def callee(self):
        raise ftplib.error_perm()

    def test_ftplib_error_to_ftp_os_error(self):
        """
        Ensure the `ftplib` exception isn't used as `FTPOSError` argument.
        """
        with pytest.raises(ftputil.error.FTPOSError) as exc_info:
            with ftputil.error.ftplib_error_to_ftp_os_error:
                self.callee()
        exc = exc_info.value
        assert not (exc.args and isinstance(exc.args[0], ftplib.error_perm))
        del exc_info

    def test_ftplib_error_to_ftp_io_error(self):
        """
        Ensure the `ftplib` exception isn't used as `FTPIOError` argument.
        """
        with pytest.raises(ftputil.error.FTPIOError) as exc_info:
            with ftputil.error.ftplib_error_to_ftp_io_error:
                self.callee()
        exc = exc_info.value
        assert not (exc.args and isinstance(exc.args[0], ftplib.error_perm))
        del exc_info

    def test_error_message_reuse(self):
        """
        Test if the error message string is retained if the caught exception
        has more than one element in `args`.
        """
        # See ticket #76.
        with pytest.raises(ftputil.error.FTPOSError) as exc_info:
            # Format "host:port" doesn't work. The use here is intentional.
            host = ftputil.FTPHost("localhost:21", "", "")
        exc = exc_info.value
        assert isinstance(exc.__cause__, socket.gaierror)
        assert exc.__cause__.errno == socket.EAI_NONAME
        del exc_info
