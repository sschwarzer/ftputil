# Copyright (C) 2003-2021, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
ftputil.path - simulate `os.path` for FTP servers
"""

import os
import posixpath
import stat

import ftputil.error
import ftputil.tool


# The `_Path` class shouldn't be used directly by clients of the ftputil
# library.
__all__ = []


class _Path:
    """
    Support class resembling `os.path`, accessible from the `FTPHost` object,
    e. g. as `FTPHost().path.abspath(path)`.

    Hint: substitute `os` with the `FTPHost` object.
    """

    # `_Path` needs to provide all methods of `os.path`.
    # pylint: disable=too-many-instance-attributes

    def __init__(self, host):
        self._host = host
        self._encoding = host._encoding
        # Delegate these methods to the `posixpath` module because they don't
        # need file system access but work on the path strings (possibly
        # extracted from `PathLike` objects).
        # pylint: disable=invalid-name
        pp = posixpath
        self.basename = pp.basename
        self.commonprefix = pp.commonprefix
        self.dirname = pp.dirname
        self.isabs = pp.isabs
        self.join = pp.join
        self.normcase = pp.normcase
        self.normpath = pp.normpath
        self.split = pp.split
        self.splitdrive = pp.splitdrive
        self.splitext = pp.splitext

    def abspath(self, path):
        """
        Return an absolute path.
        """
        # Don't use `raise_for_empty_path` here since Python itself doesn't
        # raise an exception and just returns the current directory.
        original_path = path
        path = ftputil.tool.as_str_path(path, encoding=self._encoding)
        if not self.isabs(path):
            path = self.join(self._host.getcwd(), path)
        return ftputil.tool.same_string_type_as(
            os.fspath(original_path), self.normpath(path), self._encoding
        )

    def exists(self, path):
        """
        Return true if the path exists.
        """
        if path in ["", b""]:
            return False
        try:
            lstat_result = self._host.lstat(path, _exception_for_missing_path=False)
            return lstat_result is not None
        except ftputil.error.RootDirError:
            return True

    def getmtime(self, path):
        """
        Return the timestamp for the last modification for `path` as a float.

        This will raise `PermanentError` if the path doesn't exist, but maybe
        other exceptions depending on the state of the server (e. g. timeout).
        """
        ftputil.tool.raise_for_empty_path(path)
        return self._host.stat(path).st_mtime

    def getsize(self, path):
        """
        Return the size of the `path` item as an integer.

        This will raise `PermanentError` if the path doesn't exist, but maybe
        raise other exceptions depending on the state of the server (e. g.
        timeout).
        """
        ftputil.tool.raise_for_empty_path(path)
        return self._host.stat(path).st_size

    # Check whether a path is a regular file/dir/link. For the first two cases
    # follow links (like in `os.path`).
    #
    # Implementation note: The previous implementations simply called `stat` or
    # `lstat` and returned `False` if they ended with raising a
    # `PermanentError`. That exception usually used to signal a missing path.
    # This approach has the problem, however, that exceptions caused by code
    # earlier in `lstat` are obscured by the exception handling in `isfile`,
    # `isdir` and `islink`.

    def _is_file_system_entity(self, path, dir_or_file):
        """
        Return `True` if `path` represents the file system entity described by
        `dir_or_file` ("dir" or "file").

        Return `False` if `path` isn't a directory or file, respectively or if
        `path` leads to an infinite chain of links.
        """
        assert dir_or_file in ["dir", "file"]
        # Consider differences between directories and files.
        if dir_or_file == "dir":
            should_look_for_dir = True
            stat_function = stat.S_ISDIR
        else:
            should_look_for_dir = False
            stat_function = stat.S_ISREG
        #
        path = ftputil.tool.as_str_path(path, encoding=self._encoding)
        #  Workaround if we can't go up from the current directory. The result
        #  from `getcwd` should already be normalized.
        if self.normpath(path) == self._host.getcwd():
            return should_look_for_dir
        try:
            stat_result = self._host.stat(path, _exception_for_missing_path=False)
        except ftputil.error.RecursiveLinksError:
            return False
        except ftputil.error.RootDirError:
            return should_look_for_dir
        else:
            if stat_result is None:
                # Non-existent path
                return False
            else:
                return stat_function(stat_result.st_mode)

    def isdir(self, path):
        """
        Return true if the `path` exists and corresponds to a directory (no
        link).

        A non-existing path does _not_ cause a `PermanentError`, instead return
        `False`.
        """
        if path in ["", b""]:
            return False
        return self._is_file_system_entity(path, "dir")

    def isfile(self, path):
        """
        Return true if the `path` exists and corresponds to a regular file (no
        link).

        A non-existing path does _not_ cause a `PermanentError`, instead return
        `False`.
        """
        if path in ["", b""]:
            return False
        return self._is_file_system_entity(path, "file")

    def islink(self, path):
        """
        Return true if the `path` exists and is a link.

        A non-existing path does _not_ cause a `PermanentError`, instead return
        `False`.
        """
        path = ftputil.tool.as_str_path(path, encoding=self._encoding)
        if path == "":
            return False
        try:
            lstat_result = self._host.lstat(path, _exception_for_missing_path=False)
        except ftputil.error.RootDirError:
            return False
        else:
            if lstat_result is None:
                # Non-existent path
                return False
            else:
                return stat.S_ISLNK(lstat_result.st_mode)

    def walk(self, top, func, arg):
        """
        Directory tree walk with callback function.

        For each directory in the directory tree rooted at top
        (including top itself, but excluding "." and ".."), call
        func(arg, dirname, fnames). dirname is the name of the
        directory, and fnames a list of the names of the files and
        subdirectories in dirname (excluding "." and "..").  func may
        modify the fnames list in-place (e.g. via del or slice
        assignment), and walk will only recurse into the
        subdirectories whose names remain in fnames; this can be used
        to implement a filter, or to impose a specific order of
        visiting.  No semantics are defined for, or required of, arg,
        beyond that arg is always passed to func.  It can be used,
        e.g., to pass a filename pattern, or a mutable object designed
        to accumulate statistics.  Passing None for arg is common.
        """
        ftputil.tool.raise_for_empty_path(top, path_argument_name="top")
        top = ftputil.tool.as_str_path(top, encoding=self._encoding)
        # This code (and the above documentation) is taken from `posixpath.py`,
        # with slight modifications.
        try:
            names = self._host.listdir(top)
        except OSError:
            return
        func(arg, top, names)
        for name in names:
            name = self.join(top, name)
            try:
                stat_result = self._host.lstat(name)
            except OSError:
                continue
            if stat.S_ISDIR(stat_result[stat.ST_MODE]):
                self.walk(name, func, arg)
