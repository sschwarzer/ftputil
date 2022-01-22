# Copyright (C) 2003-2022, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
ftputil.file - support for file-like objects on FTP servers
"""

import ftputil.error


# This module shouldn't be used by clients of the ftputil library.
__all__ = []


try:
    import ssl
except ImportError:
    SSLSocket = None
else:
    SSLSocket = ssl.SSLSocket


class FTPFile:
    """
    Represents a file-like object associated with an FTP host. File and socket
    are closed appropriately if the `close` method is called.
    """

    # Set timeout in seconds when closing file connections (see ticket #51).
    _close_timeout = 5

    def __init__(self, host):
        """Construct the file(-like) object."""
        self._host = host
        # pylint: disable=protected-access
        self._session = host._session
        # The file is still closed.
        self.closed = True
        self._conn = None
        self._fobj = None

    def _open(
        self,
        path,
        mode,
        buffering=None,
        encoding=None,
        errors=None,
        newline=None,
        *,
        rest=None,
    ):
        """
        Open the remote file with given path name and mode.

        Contrary to the `open` builtin, this method returns `None`, instead
        this file object is modified in-place.
        """
        # We use the same arguments as in `open`.
        # pylint: disable=unused-argument
        # pylint: disable=too-many-arguments
        #
        # Check mode.
        if mode is None:
            # This is Python's behavior for local files.
            raise TypeError("open() argument 2 must be str, not None")
        if "a" in mode:
            raise ftputil.error.FTPIOError("append mode not supported")
        if mode not in ("r", "rb", "rt", "w", "wb", "wt"):
            raise ftputil.error.FTPIOError("invalid mode '{}'".format(mode))
        if "b" in mode and "t" in mode:
            # Raise a `ValueError` like Python would.
            raise ValueError("can't have text and binary mode at once")
        # Convenience variables
        is_binary_mode = "b" in mode
        is_read_mode = "r" in mode
        # `rest` is only allowed for binary mode.
        if (not is_binary_mode) and (rest is not None):
            raise ftputil.error.CommandNotImplementedError(
                "`rest` argument can't be used for text files"
            )
        # Always use binary mode and leave any conversions to Python,
        # controlled by the arguments to `makefile` below.
        transfer_type = "I"
        command = "TYPE {}".format(transfer_type)
        with ftputil.error.ftplib_error_to_ftp_io_error:
            self._session.voidcmd(command)
        # Make transfer command.
        command_type = "RETR" if is_read_mode else "STOR"
        command = "{} {}".format(command_type, path)
        # Get connection and file object.
        with ftputil.error.ftplib_error_to_ftp_io_error:
            self._conn = self._session.transfercmd(command, rest)
        self._fobj = self._conn.makefile(
            mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline
        )
        # This comes last so that `close` won't try to close `FTPFile` objects
        # without `_conn` and `_fobj` attributes in case of an error.
        self.closed = False

    def __iter__(self):
        """
        Return a file iterator.
        """
        return self

    def __next__(self):
        """
        Return the next line or raise `StopIteration`, if there are no more.
        """
        # Apply implicit line ending conversion for text files.
        line = self.readline()
        if line:
            return line
        else:
            raise StopIteration

    #
    # Context manager methods
    #
    def __enter__(self):
        # Return `self`, so it can be accessed as the variable component of the
        # `with` statement.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # We don't need the `exc_*` arguments here
        # pylint: disable=unused-argument
        self.close()
        # Be explicit
        return False

    #
    # Other attributes
    #
    def __getattr__(self, attr_name):
        """
        Handle requests for attributes unknown to `FTPFile` objects: delegate
        the requests to the contained file object.
        """
        if attr_name in (
            "encoding flush isatty fileno read readline readlines seek tell "
            "truncate name softspace write writelines".split()
        ):
            return getattr(self._fobj, attr_name)
        raise AttributeError("'FTPFile' object has no attribute '{}'".format(attr_name))

    # TODO: Implement `__dir__`? (See
    # http://docs.python.org/whatsnew/2.6.html#other-language-changes )

    def close(self):
        """
        Close the `FTPFile`.
        """
        if self.closed:
            return
        # Timeout value to restore, see below.
        # Statement works only before the try/finally statement, otherwise
        # Python raises an `UnboundLocalError`.
        old_timeout = self._session.sock.gettimeout()
        try:
            self._fobj.close()
            self._fobj = None
            with ftputil.error.ftplib_error_to_ftp_io_error:
                if (SSLSocket is not None) and isinstance(self._conn, SSLSocket):
                    self._conn.unwrap()
                self._conn.close()
            # Set a timeout to prevent waiting until server timeout if we have
            # a server blocking here like in ticket #51.
            self._session.sock.settimeout(self._close_timeout)
            try:
                with ftputil.error.ftplib_error_to_ftp_io_error:
                    self._session.voidresp()
            except ftputil.error.FTPIOError as exc:
                # Ignore some errors, see tickets #51 and #17 at
                # http://ftputil.sschwarzer.net/trac/ticket/51 and
                # http://ftputil.sschwarzer.net/trac/ticket/17, respectively.
                exc = str(exc)
                error_code = exc[:3]
                if exc.splitlines()[0] != "timed out" and error_code not in (
                    "150",
                    "426",
                    "450",
                    "451",
                ):
                    raise
        finally:
            # Restore timeout for socket of `FTPFile`'s `ftplib.FTP` object in
            # case the connection is reused later.
            self._session.sock.settimeout(old_timeout)
            # If something went wrong before, the file is probably defunct and
            # subsequent calls to `close` won't help either, so we consider the
            # file closed for practical purposes.
            self.closed = True

    def __getstate__(self):
        raise TypeError("cannot serialize FTPFile object")
