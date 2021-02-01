# Copyright (C) 2003-2021, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
ftputil.error - exception classes and wrappers
"""

# pylint: disable=too-many-ancestors

import ftplib

import ftputil.path_encoding
import ftputil.tool
import ftputil.version


# You _can_ import these with `from ftputil.error import *`, - but it's _not_
# recommended.
__all__ = [
    "CommandNotImplementedError",
    "FTPIOError",
    "FTPOSError",
    "InaccessibleLoginDirError",
    "InternalError",
    "KeepAliveError",
    "NoEncodingError",
    "ParserError",
    "PermanentError",
    "RootDirError",
    "SyncError",
    "TemporaryError",
    "TimeShiftError",
]


class FTPError(Exception):
    """
    General ftputil error class.
    """

    def __init__(self, *args, original_error=None):
        super().__init__(*args)
        # `strerror`
        self.strerror = ""
        if original_error is not None:
            try:
                self.strerror = str(original_error)
            except Exception:
                # Consume all errors. If the `str` call fails, it's more
                # appropriate to ignore `original_error` than to raise an
                # exception while instantiating `FTPError`.
                pass
        elif args:
            # Assume the first argument is a string. It may be a byte string
            # though.
            try:
                self.strerror = ftputil.tool.as_str(
                    args[0], ftputil.path_encoding.DEFAULT_ENCODING
                )
            except TypeError:
                # `args[0]` isn't `str` or `bytes`.
                pass
        # `errno`
        self.errno = None
        try:
            self.errno = int(self.strerror[:3])
        except ValueError:
            # `int()` argument couldn't be converted to an integer.
            pass
        # `file_name`
        self.file_name = None

    def __str__(self):
        return "{}\nDebugging info: {}".format(
            self.strerror, ftputil.version.version_info
        )


# Internal errors are those that have more to do with the inner workings of
# ftputil than with errors on the server side.
class InternalError(FTPError):
    """Internal error."""

    pass


class RootDirError(InternalError):
    """Raised for generic stat calls on the remote root directory."""

    pass


class InaccessibleLoginDirError(InternalError):
    """May be raised if the login directory isn't accessible."""

    pass


class TimeShiftError(InternalError):
    """Raised for invalid time shift values."""

    pass


class ParserError(InternalError):
    """Raised if a line of a remote directory can't be parsed."""

    pass


class CacheMissError(InternalError):
    """Raised if a path isn't found in the cache."""

    pass


class NoEncodingError(InternalError):
    """Raised if session instances don't specify an encoding."""

    pass


# Currently not used
class KeepAliveError(InternalError):
    """Raised if the keep-alive feature failed."""

    pass


class FTPOSError(FTPError, OSError):
    """Generic FTP error related to `OSError`."""

    pass


class TemporaryError(FTPOSError):
    """Raised for temporary FTP errors (4xx)."""

    pass


class PermanentError(FTPOSError):
    """Raised for permanent FTP errors (5xx)."""

    pass


class CommandNotImplementedError(PermanentError):
    """Raised if the server doesn't implement a certain feature (502)."""

    pass


class RecursiveLinksError(PermanentError):
    """Raised if an infinite link structure is detected."""

    pass


# Currently not used
class SyncError(PermanentError):
    """Raised for problems specific to syncing directories."""

    pass


class FtplibErrorToFTPOSError:
    """
    Context manager to convert `ftplib` exceptions to exceptions derived from
    `FTPOSError`.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            # No exception
            return
        if isinstance(exc_value, ftplib.error_temp):
            raise TemporaryError(
                *exc_value.args, original_error=exc_value
            ) from exc_value
        elif isinstance(exc_value, ftplib.error_perm):
            # If `exc_value.args[0]` is present, assume it's a byte or unicode
            # string.
            if exc_value.args and ftputil.tool.as_str(
                exc_value.args[0], ftputil.path_encoding.DEFAULT_ENCODING
            ).startswith("502"):
                raise CommandNotImplementedError(
                    *exc_value.args, original_error=exc_value
                ) from exc_value
            else:
                raise PermanentError(
                    *exc_value.args, original_error=exc_value
                ) from exc_value
        elif isinstance(exc_value, ftplib.all_errors):
            raise FTPOSError(*exc_value.args, original_error=exc_value) from exc_value
        else:
            raise


ftplib_error_to_ftp_os_error = FtplibErrorToFTPOSError()


class FTPIOError(FTPError, IOError):
    """Generic FTP error related to `IOError`."""

    pass


class FtplibErrorToFTPIOError:
    """
    Context manager to convert `ftplib` exceptions to `FTPIOError` exceptions.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            # No exception
            return
        if isinstance(exc_value, ftplib.all_errors):
            raise FTPIOError(*exc_value.args, original_error=exc_value) from exc_value
        else:
            raise


ftplib_error_to_ftp_io_error = FtplibErrorToFTPIOError()
