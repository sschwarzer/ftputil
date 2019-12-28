# Copyright (C) 2013-2018, Stefan Schwarzer
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
tool.py - helper code
"""

__all__ = ["same_string_type_as", "as_bytes", "as_unicode", "as_default_string"]


# Encoding to convert between byte string and unicode string. This is
# a "lossless" encoding: Strings can be encoded/decoded back and forth
# without information loss or causing encoding-related errors. The
# `ftplib` module under Python 3 also uses the "latin1" encoding
# internally. It's important to use the same encoding here, so that users who
# used `ftplib` to create FTP items with non-ASCII characters can access them
# in the same way with ftputil.
LOSSLESS_ENCODING = "latin1"


def same_string_type_as(type_source, content_source):
    """
    Return a string of the same type as `type_source` with the content
    from `content_source`.

    If the `type_source` and `content_source` don't have the same
    type, use `LOSSLESS_ENCODING` above to encode or decode, whatever
    operation is needed.
    """
    if isinstance(type_source, bytes) and isinstance(content_source, str):
        return content_source.encode(LOSSLESS_ENCODING)
    elif isinstance(type_source, str) and isinstance(content_source, bytes):
        return content_source.decode(LOSSLESS_ENCODING)
    else:
        return content_source


def as_bytes(string):
    """
    Return the argument `string` converted to a byte string if it's a
    unicode string. Otherwise just return the string.
    """
    return same_string_type_as(b"", string)


def as_unicode(string):
    """
    Return the argument `string` converted to a unicode string if it's
    a byte string. Otherwise just return the string.
    """
    return same_string_type_as("", string)


def as_default_string(string):
    """
    Return the argument `string` converted to a the default string
    type for the Python version. For unicode strings,
    `LOSSLESS_ENCODING` is used for encoding or decoding.
    """
    return same_string_type_as("", string)


def encode_if_unicode(string, encoding):
    """
    Return the string `string`, encoded with `encoding` if `string` is
    a unicode string. Otherwise return `string` unchanged.
    """
    if isinstance(string, str):
        return string.encode(encoding)
    else:
        return string
