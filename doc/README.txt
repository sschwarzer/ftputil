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

Since version 3.1 the following changed:

- For some platforms (notably Windows) modification datetimes before
  the epoch would cause an `OverflowError` [1]. Other platforms could
  return negative values. Since the Python documentation for the
  `time` module [2] points out that values before the epoch might
  cause problems, ftputil now sets the float value for such datetimes
  to 0.0.

  In theory, this might cause backward compatibility problems, but
  it's very unlikely since pre-epoch timestamps in directory listings
  should be very rare.

- On some platforms, the `time.mktime` implementation could behave
  strange and accept invalid date/time values. For example, a day
  value of 32 would be accepted and implicitly cause a "wrap" to the
  next month. Such invalid values now result in a `ParserError`.

- Make error handling more robust where the underlying FTP session
  factory (for example, `ftplib.FTP`) uses byte strings for exception
  messages. [3]

- Improved error handling for directory listings. As just one example,
  previously a non-integer value for a day would unintentionally cause
  a `ValueError`. Now this causes a `ParserError`.

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

To use ftputil, you need Python, at least version 2.6. Python 3.x
versions work as well. Python is a programming language, available
from http://www.python.org for free.

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

[1] http://ftputil.sschwarzer.net/trac/ticket/83
[2] https://docs.python.org/3/library/time.html
[3] http://ftputil.sschwarzer.net/trac/ticket/85
