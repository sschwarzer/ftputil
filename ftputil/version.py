# Copyright (C) 2006-2018, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Provide version information about ftputil and the runtime environment.
"""

import sys


# ftputil version number; substituted by `make patch`
__version__ = "5.1.0"

_ftputil_version = __version__
_python_version = sys.version.split()[0]
_python_platform = sys.platform


version_info = "ftputil {}, Python {} ({})".format(
    _ftputil_version, _python_version, _python_platform
)
