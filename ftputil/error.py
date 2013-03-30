# Copyright (C) 2003-2013, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# See the file LICENSE for licensing terms.

"""
ftputil.error - exception classes and wrappers
"""

# "Too many ancestors"
# pylint: disable = R0901
#
# "Used * or ** magic"
# pylint: disable = W0142

import ftplib
import sys

import ftputil.version


# You _can_ import these with `from ftputil.error import *`, - but
# it's _not_ recommended.
__all__ = [
  'FTPError',
  'InternalError',
  'RootDirError',
  'InaccessibleLoginDirError',
  'TimeShiftError',
  'ParserError',
  'KeepAliveError',
  'FTPOSError',
  'TemporaryError',
  'PermanentError',
  'CommandNotImplementedError',
  'SyncError',
  'FTPIOError',
  ]


class FTPError(Exception):
    """General ftputil error class."""

    def __init__(self, *args):
        try:
            # Works only for new style-classes (Python 2.5+). Before,
            # `Exception` was a classic class.
            super(FTPError, self).__init__(*args)
        except TypeError:
            # Fallback to old approach.
            Exception.__init__(self, *args)
        # Don't use `args[0]` directly because `args` may be empty.
        if args:
            self.strerror = self.args[0]
        else:
            self.strerror = ""
        try:
            self.errno = int(self.strerror[:3])
        except (TypeError, IndexError, ValueError):
            self.errno = None
        self.filename = None

    def __str__(self):
        return "%s\nDebugging info: %s" % \
               (self.strerror, ftputil.version.version_info)


# Internal errors are those that have more to do with the inner
# workings of ftputil than with errors on the server side.
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

# Currently not used
class SyncError(PermanentError):
    """Raised for problems specific to syncing directories."""
    pass


class FtplibErrorToFTPOSError(object):
    """
    Context manager to convert `ftplib` exceptions to exceptions
    derived from `FTPOSError`.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            # No exception
            return
        if isinstance(exc_value, ftplib.error_temp):
            raise TemporaryError(*exc_value.args)
        elif isinstance(exc_value, ftplib.error_perm):
            # If `exc_value.args` is present, assume it's a byte or
            # unicode string.
            if exc_value.args and exc_value.args[0].startswith("502"):
                raise CommandNotImplementedError(*exc_value.args)
            else:
                raise PermanentError(*exc_value.args)
        elif isinstance(exc_value, ftplib.all_errors):
            raise FTPOSError(*exc_value.args)
        else:
            raise

ftplib_error_to_ftp_os_error = FtplibErrorToFTPOSError()


class FTPIOError(FTPError, IOError):
    """Generic FTP error related to `IOError`."""
    pass


class FtplibErrorToFTPIOError(object):
    """
    Context manager to convert `ftplib` exceptions to `FTPIOError`
    exceptions.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            # No exception
            return
        if isinstance(exc_value, ftplib.all_errors):
            raise FTPIOError(*exc_value.args)
        else:
            raise

ftplib_error_to_ftp_io_error = FtplibErrorToFTPIOError()
