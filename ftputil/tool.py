# Copyright (C) 2013-2021, Stefan Schwarzer
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
tool.py - helper code
"""

import os


__all__ = ["same_string_type_as", "as_str", "as_str_path", "raise_for_empty_path"]


def same_string_type_as(type_source, string, encoding):
    """
    Return a string of the same type as `type_source` with the content from
    `string`.

    If the `type_source` and `string` don't have the same type, use `encoding`
    to encode or decode, whatever operation is needed.
    """
    if isinstance(type_source, bytes) and isinstance(string, str):
        return string.encode(encoding)
    elif isinstance(type_source, str) and isinstance(string, bytes):
        return string.decode(encoding)
    else:
        return string


def as_str(string, encoding):
    """
    Return the argument `string` converted to a unicode string if it's a
    `bytes` object. Otherwise just return the string.

    If a conversion is necessary, use `encoding`.

    If `string` is neither `str` nor `bytes`, raise a `TypeError`.
    """
    if isinstance(string, bytes):
        return string.decode(encoding)
    elif isinstance(string, str):
        return string
    else:
        raise TypeError("`as_str` argument must be `bytes` or `str`")


def as_str_path(path, encoding):
    """
    Return the argument `path` converted to a unicode string if it's a `bytes`
    object. Otherwise just return the string.

    If a conversion is necessary, use `encoding`.

    Instead of passing a `bytes` or `str` object for `path`, you can pass a
    `PathLike` object that can be converted to a `bytes` or `str` object.

    If the `path` can't be converted to a `bytes` or `str`, a `TypeError` is
    raised.
    """
    path = os.fspath(path)
    return as_str(path, encoding)


def raise_for_empty_path(path, path_argument_name="path"):
    """
    Raise an exception of class `exception_class` if `path` is an empty string
    (text or bytes).
    """
    # Avoid cyclic import.
    import ftputil.error

    # Don't handle `pathlib.Path("")`. This immediately results in `Path(".")`,
    # so we can't detect it anyway. Regarding bytes, `Path(b"")` results in a
    # `TypeError`.
    if path in ["", b""]:
        if path_argument_name is None:
            message = "path argument is empty"
        else:
            message = f"path argument `{path_argument_name}` is empty"
        raise ftputil.error.FTPIOError(message)
