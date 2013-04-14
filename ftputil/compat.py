# encoding: utf-8
# Copyright (C) 2011-2013, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# See the file LICENSE for licensing terms.

"""
Functions to make the same code work in both Python 2 and 3.

The comments given for the Python 2 versions of the helpers apply to
the Python 3 helpers as well.
"""

from __future__ import unicode_literals

import sys


python_version = sys.version_info[0]


if python_version == 2:

    int_types = (int, long)

    unicode_type = unicode
    bytes_type = str

    # Non-evaluating input
    input = raw_input

else:

    int_types = (int,)

    unicode_type = str
    bytes_type = bytes

    input = input

# For Python 2 `str` means byte strings, for Python 3 unicode strings.
default_string_type = str
