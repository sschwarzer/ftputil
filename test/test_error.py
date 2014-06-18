# encoding: utf-8
# Copyright (C) 2002-2014, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

from __future__ import unicode_literals

import ftplib
import unittest

import ftputil.error


class TestFTPErrorArguments(unittest.TestCase):
    """
    The `*Error` constructors should accept either a byte string or a
    unicode string.
    """

    def test_bytestring_argument(self):
        # An umlaut as latin-1 character
        io_error = ftputil.error.FTPIOError(b"\xe4")
        os_error = ftputil.error.FTPOSError(b"\xe4")

    def test_unicode_argument(self):
        # An umlaut as unicode character
        io_error = ftputil.error.FTPIOError("\xe4")
        os_error = ftputil.error.FTPOSError("\xe4")


class TestErrorConversion(unittest.TestCase):

    def callee(self):
        raise ftplib.error_perm()

    def test_ftplib_error_to_ftp_os_error(self):
        """
        Ensure the `ftplib` exception isn't used as `FTPOSError`
        argument.
        """
        try:
            with ftputil.error.ftplib_error_to_ftp_os_error:
                self.callee()
        except ftputil.error.FTPOSError as exc:
            self.assertFalse(exc.args and
                             isinstance(exc.args[0], ftplib.error_perm))
        else:
            # We shouldn't come here.
            self.fail()

    def test_ftplib_error_to_ftp_os_error_non_ascii_server_message(self):
        """
        Test that we don't get a `UnicodeDecodeError` if the server
        sends a message containing non-ASCII characters.
        """
        # See ticket #77.
        message = \
          ftputil.tool.as_bytes("Não é possível criar um arquivo já existente.")
        try:
            with ftputil.error.ftplib_error_to_ftp_os_error:
                raise ftplib.error_perm(message)
        # We expect a `PermanentError`.
        except ftputil.error.PermanentError:
            pass
        except UnicodeDecodeError:
            self.fail()

    def test_ftplib_error_to_ftp_io_error(self):
        """
        Ensure the `ftplib` exception isn't used as `FTPIOError`
        argument.
        """
        try:
            with ftputil.error.ftplib_error_to_ftp_io_error:
                self.callee()
        except ftputil.error.FTPIOError as exc:
            self.assertFalse(exc.args and
                             isinstance(exc.args[0], ftplib.error_perm))
        else:
            # We shouldn't come here.
            self.fail()

    def test_error_message_reuse(self):
        """
        Test if the error message string is retained if the caught
        exception has more than one element in `args`.
        """
        # See ticket #76.
        try:
            # Format "host:port" doesn't work.
            host = ftputil.FTPHost("localhost:21", "", "")
        except ftputil.error.FTPOSError as exc:
            # The error message might change for future Python
            # versions, so possibly relax the assertion later.
            self.assertTrue("[Errno -2] Name or service not known" in
                            str(exc))


if __name__ == "__main__":
    unittest.main()
