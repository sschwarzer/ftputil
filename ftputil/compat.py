# encoding: utf-8
# Copyright (C) 2011, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# See the file LICENSE for licensing terms.

"""
Some functions to make the code work also on Python 3 after applying
the 2to3 utility.

The comments given for the Python 2 versions of the helpers apply to
the Python 3 helpers as well.
"""

# Note that more imports are to be found in the large `if`
# statement below, because they work only in Python 2 or
# Python 3.
import sys


if sys.version_info[0] == 2:

    # As a low-level networking library, ftputil mostly works on
    # byte strings, so 2to3's approach to turn byte strings into
    # unicode strings won't work most of the time.
    def b(byte_string):
        return byte_string

    # Similarly for `StringIO` and such.
    import StringIO
    byte_string_io = StringIO.StringIO

else:

    def b(byte_string):
        return bytes(byte_string, encoding="ASCII")

    import io
    byte_string_io = io.BytesIO
