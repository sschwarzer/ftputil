# Copyright (C) 2013-2019, Stefan Schwarzer
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
tool.py - helper code
"""

import os


__all__ = ["same_string_type_as", "as_bytes", "as_str"]


# Encoding to convert between byte string and unicode string. This is
# a "lossless" encoding: Strings can be encoded/decoded back and forth
# without information loss or causing encoding-related errors. The
# `ftplib` module under Python 3 also uses the "latin1" encoding
# internally. It's important to use the same encoding here, so that users who
# used `ftplib` to create FTP items with non-ASCII characters can access them
# in the same way with ftputil.
LOSSLESS_ENCODING = "latin1"


def same_string_type_as(type_source, path):
    """
    Return a string of the same type as `type_source` with the content
    from `path`.

    `type_source` may be a `PathLike` object. In that case, the type
    source is determined as `type_source.__fspath__()`.

    If the `type_source` (possibly after the described transformation)
    and `content_source` don't have the same type, use
    `LOSSLESS_ENCODING` above to encode or decode, whatever operation
    is needed.

    If the `path` can't be converted to a `bytes` or `str`, a `TypeError`
    is raised.
    """
    actual_type_source = os.fspath(type_source)
    if isinstance(actual_type_source, bytes) and isinstance(path, str):
        return path.encode(LOSSLESS_ENCODING)
    elif isinstance(actual_type_source, str) and isinstance(path, bytes):
        return path.decode(LOSSLESS_ENCODING)
    else:
        return path


def as_bytes(string):
    """
    Return the argument `string` converted to a `bytes` object if it's
    a unicode string. Otherwise just return the `bytes` object.
    """
    return same_string_type_as(b"", string)


def as_str(string):
    """
    Return the argument `string` converted to a unicode string if it's
    a `bytes` object. Otherwise just return the string.
    """
    return same_string_type_as("", string)
