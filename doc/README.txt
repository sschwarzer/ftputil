ftputil
=======

Purpose
-------

ftputil is a high-level FTP client library for the Python programming
language. ftputil implements a virtual file system for accessing FTP
servers, that is, it can generate file-like objects for remote files.
The library supports many functions similar to those in the os,
os.path and shutil modules. ftputil has convenience functions for
conditional uploads and downloads, and handles FTP clients and servers
in different timezones.

What's new?
-----------

Backward-incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This ftputil version isn't fully backward-compatible with the previous
version. The backward-incompatible changes are:

- Python 2 is no longer supported.

- The minimal supported Python 3 version is 3.6.

- The flag `use_list_a_option` of `FTPHost` instances is now set to
  `False` by default. This option was intended to make life easier for
  users, but turned out to be problematic [1].

- By default, time stamps in directory listings coming from the server
  are now assumed to be in UTC. Previously, listings were assumed to
  use the local time of the client. [2]

  Correspondingly, the definition of "time shift" has changed. The
  time shift is now defined as the time zone used in server listings
  (say, UTC+02:00) and UTC, in other words, the time shift now is the
  time zone offset applied in the server listings. In earlier ftputil
  versions, the time shift was defined as "time used in server
  listings" minus "local client time."

If you need to use Python versions before 3.6, please use the previous
stable ftputil version 3.4.

Other changes
~~~~~~~~~~~~~

- Functions and methods which used to accept only `str` or `bytes`
  paths now _also_ accept `PathLike` objects [3, 4].

- `FTPHost.makedirs` correctly handles `exist_ok`. [5]

- Clear the stat cache when setting a new time shift value. [6]

- ftputil now officially follows semantic versioning (SemVer) [7].
  Actually ftputil has been following semantic versioning since a long
  time (probably since version 2.0 in 2004), but it was never
  explicitly guaranteed and new major versions were named x.0 instead
  of x.0.0 and new minor versions x.y instead of x.y.0.

- Internal changes: The tests were moved to pytest. The old mocking
  approach was replaced by a "scripted session" approach.

Documentation
-------------

The documentation for ftputil can be found in the file ftputil.txt
(reStructuredText format) or ftputil.html (recommended, generated from
ftputil.txt).

Prerequisites
-------------

To use ftputil, you need Python, at least version 3.5.

Installation
------------

*If you have an older version of ftputil installed, delete it or
move it somewhere else, so that it doesn't conflict with the new
version!*

If you have pip or easy_install available, you can install the current
version of ftputil directly from the Python Package Index (PyPI)
without downloading the package explicitly. You'll still need an
internet connection, of course.

- Just type

    pip install ftputil
  
  or
  
    easy_install ftputil
  
  on the command line, respectively. Unless you're installing ftputil
  in a virtual environment, you'll probably need root/administrator
  privileges to do that.
  
  Done. :-)

If you don't have pip or easy_install, you need to download a tarball
from the Python Package Index or from the ftputil website and install
it:

- Unpack the archive file containing the distribution files. If you
  had an ftputil version 2.8, you would type at the shell prompt:

    tar xzf ftputil-2.8.tar.gz

- Make the directory to where the files were unpacked your current
  directory. Assume that after unpacking, you have a directory
  `ftputil-2.8`. Make it the current directory with

    cd ftputil-2.8

- Type

    python setup.py install

  at the shell prompt. On Unix/Linux, you have to be root to perform
  the installation. Likewise, you have to be logged in as
  administrator if you install on Windows.

  If you want to customize the installation paths, please read
  http://docs.python.org/inst/inst.html .

License
-------

ftputil is open source software. It is distributed under the
new/modified/revised BSD license (see
http://opensource.org/licenses/BSD-3-Clause ).

Authors
-------

Stefan Schwarzer <sschwarzer@sschwarzer.net>

Evan Prodromou <evan@bad.dynu.ca> (lrucache module)

(See also the file `doc/contributors.txt`.)

Please provide feedback! It's certainly appreciated. :-)


[1] https://ftputil.sschwarzer.net/trac/ticket/110
[2] https://ftputil.sschwarzer.net/trac/ticket/134
[3] https://docs.python.org/3/library/os.html#os.PathLike
[4] https://ftputil.sschwarzer.net/trac/ticket/119
[5] https://ftputil.sschwarzer.net/trac/ticket/117
[6] https://ftputil.sschwarzer.net/trac/ticket/136
[7] https://semver.org/
