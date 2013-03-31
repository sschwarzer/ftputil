# Copyright (C) 2013, Stefan Schwarzer
# See the file LICENSE for licensing terms.

"""
tool.py - helper code
"""

from __future__ import unicode_literals

import ftputil.compat as compat


__all__ = ["same_string_type_as"]


# Encoding to convert a string to the same type as another. This is a
# "lossless" encoding: Strings can be encoded/decoded back and forth
# without information loss or causing encoding-related errors. The
# `ftplib` module under Python 3 also uses the "latin1" encoding.
ENCODING = "latin1"


def same_string_type_as(type_source, content_source):
    """
    Return a string of the same type as `type_source` with the content
    from `content_source`.

    If the `type_source` and `content_source` don't have the same
    type, use `ENCODING` above to encode or decode, whatever operation
    is needed.
    """
    if (
      isinstance(type_source, compat.bytes_type) and
      isinstance(content_source, compat.unicode_type)):
        return content_source.encode(ENCODING)
    elif (
      isinstance(type_source, compat.unicode_type) and
      isinstance(content_source, compat.bytes_type)):
        return content_source.decode(ENCODING)
    else:
        return content_source


def to_bytes_type(string):
    """
    Return the argument `string` converted to a byte string if it's a
    unicode string. Otherwise just return the string.
    """
    return same_string_type_as(b"", string)


def to_unicode_type(string):
    """
    Return the argument `string` converted to a unicode string if it's
    a byte string. Otherwise just return the string.
    """
    return same_string_type_as("", string)
