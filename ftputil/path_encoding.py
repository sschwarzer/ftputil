# Copyright (C) 2021, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Compatibility code for Python versions <= 3.8 vs. >= 3.9

Python 3.9 changed the default encoding for FTP remote paths from latin-1 to
UTF-8 which causes a few headaches for ftputil.
"""

import sys


__all__ = ["DEFAULT_ENCODING", "RUNNING_UNDER_PY39_AND_UP", "FTPLIB_DEFAULT_ENCODING"]


RUNNING_UNDER_PY39_AND_UP = (sys.version_info.major, sys.version_info.minor) >= (3, 9)

# FTP path default encoding for Python 3.8 and below
FTPLIB_PY38_ENCODING = "latin-1"

# FTP path default encoding for Python 3.9 and above
FTPLIB_PY39_ENCODING = "utf-8"

# Default encoding for ftputil. Stay compatible to the behavior of former
# ftputil versions and Python <= 3.8.
DEFAULT_ENCODING = FTPLIB_PY38_ENCODING

if RUNNING_UNDER_PY39_AND_UP:
    FTPLIB_DEFAULT_ENCODING = FTPLIB_PY39_ENCODING
else:
    FTPLIB_DEFAULT_ENCODING = FTPLIB_PY38_ENCODING
