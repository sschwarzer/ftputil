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

Since version 3.0 the following changed:

- Added support for `followlinks` parameter in `FTPHost.walk`. [1]

- Trying to pickle `FTPHost` and `FTPFile` objects now raises explicit
  `TypeError`s to make clear that not being able to pickle these
  objects is intentional. [2]

- Improved exception messages for socket errors [3].

- Fixed handling of server error messages with non-ASCII characters
  when running under Python 2.x. [4]

- Added a generic "session factory factory" to make creation of
  session factories easier for common use cases (encrypted
  connections, non-default port, active/passive mode, FTP session
  debug level and combination of these). [5] This includes a
  workaround for `M2Crypto.ftpslib.FTP_TLS`; this class won't be
  usable with ftputil 3.0 and up with just the session factory recipe
  described in the documentation. [6]

- Don't assume time zone differences to always be full hours, but
  rather 15-minute units. [8] For example, according to [9], Nepal's
  time zone is UTC+05:45.

- Improved documentation on timeout handling. This includes
  information on internal creation of additional FTP connections (for
  remote files, including uploads and downloads). This may help
  understand better why the `keep_alive` method is limited.

Note that ftputil 3.0 broke backward compatibility with ftputil 2.8
and before. The differences are described here:
http://ftputil.sschwarzer.net/trac/wiki/WhatsNewInFtputil3.0

Documentation
-------------

The documentation for ftputil can be found in the file ftputil.txt
(reStructuredText format) or ftputil.html (recommended, generated from
ftputil.txt).

Prerequisites
-------------

To use ftputil, you need Python, at least version 2.6. Python is a
programming language, available from http://www.python.org for free.

Installation
------------

- *If you have an older version of ftputil installed, delete it or
  move it somewhere else, so that it doesn't conflict with the new
  version!*

- Unpack the archive file containing the distribution files. If you
  had an ftputil version 2.8, you would type at the shell prompt:

    tar xzf ftputil-2.8.tar.gz

  However, if you read this, you probably unpacked the archive
  already. ;-)

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

If you have pip or easy_install installed, you can install the current
version of ftputil directly from the Python Package Index (PyPI)
without downloading the package explicitly.

- Just type

    pip install ftputil

  or

    easy_install ftputil

  on the command line, respectively. You'll probably need
  root/administrator privileges to do that (see above).

License
-------

ftputil is Open Source Software. It is distributed under the
new/modified/revised BSD license (see
http://opensource.org/licenses/BSD-3-Clause ).

Authors
-------

Stefan Schwarzer <sschwarzer@sschwarzer.net>

Evan Prodromou <evan@bad.dynu.ca> (lrucache module)

Please provide feedback! It's certainly appreciated. :-)

[1] http://ftputil.sschwarzer.net/trac/ticket/73
[2] http://ftputil.sschwarzer.net/trac/ticket/75
[3] http://ftputil.sschwarzer.net/trac/ticket/76
[4] http://ftputil.sschwarzer.net/trac/ticket/77
[5] http://ftputil.sschwarzer.net/trac/ticket/78
[6] http://ftputil.sschwarzer.net/trac/wiki/Documentation#session-factories
[7] http://ftputil.sschwarzer.net/trac/ticket/79
[8] http://ftputil.sschwarzer.net/trac/ticket/81
[9] http://en.wikipedia.org/wiki/Timezone#List_of_UTC_offsets
