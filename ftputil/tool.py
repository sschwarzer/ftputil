# Copyright (C) 2013-2021, Stefan Schwarzer
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
tool.py - helper code
"""

import os


__all__ = ["same_string_type_as", "as_str", "as_str_path"]


# Default encoding to convert between byte string and unicode string. This is a
# "lossless" encoding in the sense that any byte string can be decoded to a
# unicode string, and this unicode string can be encoded to the original byte
# string.
#
# The `ftplib` module under Python 3.8 and earlier also uses the "latin-1"
# encoding internally. In this case, paths created with Python's `ftplib` use
# the same encoding as our `DEFAULT_ENCODING`.
DEFAULT_ENCODING = "latin-1"


def same_string_type_as(type_source, string):
    """
    Return a string of the same type as `type_source` with the content from
    `string`.

    If the `type_source` and `string` don't have the same type, use
    `LOSSLESS_ENCODING` above to encode or decode, whatever operation is
    needed.
    """
    if isinstance(type_source, bytes) and isinstance(string, str):
        return string.encode(LOSSLESS_ENCODING)
    elif isinstance(type_source, str) and isinstance(string, bytes):
        return string.decode(LOSSLESS_ENCODING)
    else:
        return string


def as_str(string):
    """
    Return the argument `string` converted to a unicode string if it's a
    `bytes` object. Otherwise just return the string.

    If `string` is neither `str` nor `bytes`, raise a `TypeError`.
    """
    if isinstance(string, bytes):
        return string.decode(LOSSLESS_ENCODING)
    elif isinstance(string, str):
        return string
    else:
        raise TypeError("`as_str` argument must be `bytes` or `str`")


def as_str_path(path):
    """
    Return the argument `path` converted to a unicode string if it's a `bytes`
    object. Otherwise just return the string.

    Instead of passing a `bytes` or `str` object for `path`, you can pass a
    `PathLike` object that can be converted to a `bytes` or `str` object.

    If the `path` can't be converted to a `bytes` or `str`, a `TypeError` is
    raised.
    """
    path = os.fspath(path)
    return as_str(path)
