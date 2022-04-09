#! /usr/bin/env python
# Copyright (C) 2003-2022, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# See the file LICENSE for licensing terms.

"""
setup.py - installation script for Python distutils
"""

import os
import sys

from distutils import core


_name = "ftputil"
_package = "ftputil"
_version = open("VERSION").read().strip()


core.setup(
    # Installation data
    name=_name,
    version=_version,
    packages=[_package],
    package_dir={_package: _package},
    # Metadata
    author="Stefan Schwarzer",
    author_email="sschwarzer@sschwarzer.net",
    url="https://ftputil.sschwarzer.net/",
    description="High-level FTP client library (virtual file system and more)",
    keywords="FTP, client, library, virtual file system",
    license="Open source (revised BSD license)",
    platforms=["Pure Python"],
    # See https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires=">=3.6",
    long_description="""\
ftputil is a high-level FTP client library for the Python programming
language. ftputil implements a virtual file system for accessing FTP servers,
that is, it can generate file-like objects for remote files. The library
supports many functions similar to those in the os, os.path and
shutil modules. ftputil has convenience functions for conditional uploads
and downloads, and handles FTP clients and servers in different timezones.""",
    download_url="http://ftputil.sschwarzer.net/trac/attachment/wiki/Download/"
    "{}-{}.tar.gz?format=raw".format(_name, _version),
    classifiers=[
        # Commented-out for beta release
        "Development Status :: 5 - Production/Stable",
        #"Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems",
    ],
)
