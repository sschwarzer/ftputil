# encoding: utf-8
# Copyright (C) 2011-2013, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# See the file LICENSE for licensing terms.

"""
Some functions to make the code work also on Python 3 after applying
the 2to3 utility.

The comments given for the Python 2 versions of the helpers apply to
the Python 3 helpers as well.
"""

import sys


if sys.version_info.major == 2:

    # As a low-level networking library, ftputil mostly works on
    # byte strings, so 2to3's approach to turn byte strings into
    # unicode strings won't work most of the time.
    def b(byte_string):
        return byte_string

    int_types = (int, long)

    unicode_type = unicode
    bytes_type = str

    # Non-evaluating input
    input = raw_input

else:

    def b(byte_string):
        return bytes(byte_string, encoding="ASCII")

    int_types = (int,)

    unicode_type = str
    bytes_type = bytes

    input = input
