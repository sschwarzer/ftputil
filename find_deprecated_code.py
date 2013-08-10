#! /usr/bin/env python
# Copyright (C) 2008-2013, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# See the file LICENSE for licensing terms.

# pylint: disable=W0622

"""\
This script scans a directory tree for files which contain code which
is deprecated in ftputil %s and above (and even much longer). The
script uses simple heuristics, so it may miss occurences of deprecated
usage or print some inappropriate lines of your files.

Usage: %s start_dir

where start_dir is the starting directory which will be scanned
recursively for offending code.

Currently, these deprecated features are examined:

- You should no longer use the exceptions via the ftputil module but
  via the ftp_error module. So, for example, instead of
  ftputil.PermanentError write ftp_error.PermanentError.

- Don't use the xreadlines method of FTP file objects (as returned by
  FTPHost.file = FTPHost.open). Instead use

  for line in ftp_host.open(path):
      ...
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import sys

import ftputil.version


__doc__ = __doc__ % (ftputil.version.__version__,
                     os.path.basename(sys.argv[0]))


class DeprecatedFeature(object):

    def __init__(self, message, regex):
        self.message = message
        self.regex = regex
        # Map file name to a list of line numbers (starting at 1).
        self.locations = {}


deprecated_features = [
  DeprecatedFeature("Possible use(s) of FTP exceptions via ftputil module",
                    re.compile(r"\bftputil\s*?\.\s*?[A-Za-z]+Error\b")),
  DeprecatedFeature("Possible use(s) of ftp_error module",
                    re.compile(r"\bftp_error\b")),
  DeprecatedFeature("Possible use(s) of ftp_stat module",
                    re.compile(r"\bftp_stat\b")),
  DeprecatedFeature("Possible use(s) of FTPHost.file",
                    re.compile(r"\b(h|host|ftp|ftphost|ftp_host)\.file\(")),
  DeprecatedFeature("Possible use(s) of xreadline method of FTP file objects",
                    re.compile(r"\.\s*?xreadlines\b")),
]


def scan_file(file_name):
    """
    Scan a file with name `file_name` for code deprecated in
    ftputil usage and collect the offending data in the dictionary
    `features.locations`.
    """
    with open(file_name) as fobj:
        for index, line in enumerate(fobj, start=1):
            for feature in deprecated_features:
                if feature.regex.search(line):
                    locations = feature.locations
                    locations.setdefault(file_name, [])
                    locations[file_name].append((index, line.rstrip()))


def print_results():
    """
    Print statistics of deprecated code after the directory has been
    scanned.
    """
    last_message = ""
    for feature in deprecated_features:
        if feature.message != last_message:
            print()
            print(feature.message, "...")
            print()
            last_message = feature.message
        locations = feature.locations
        if not locations:
            print("   no deprecated code found")
            continue
        for file_name in sorted(locations.keys()):
            print(file_name)
            for line_number, line in locations[file_name]:
                print("%5d: %s" % (line_number, line))
    print()
    print("Please check your code also by other means.")


def main(start_dir):
    """
    Scan a directory tree starting at `start_dir` and print uses
    of deprecated features, if any were found.
    """
    # `dir_names` isn't used here
    # pylint: disable=W0612
    for dir_path, dir_names, file_names in os.walk(start_dir):
        for file_name in file_names:
            abs_name = os.path.abspath(os.path.join(dir_path, file_name))
            if file_name.endswith(".py"):
                scan_file(abs_name)
    print_results()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        start_dir = sys.argv[1]
        if not os.path.isdir(start_dir):
            print("Directory %s not found." % start_dir, file=sys.stderr)
            sys.exit()
    else:
        print("Usage: %s start_dir" % sys.argv[0], file=sys.stderr)
        sys.exit()
    main(start_dir)
