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
version due to changes in the `ftplib` module in the standard
library of Python 3.9 [1].

That said, if you only deal with directory and file paths which solely
consist of ASCII characters, this change doesn't affect you.

Here are some details. You can find more in the ftputil documentation
[2] and in ticket #143 [3].

Internally, ftputil uses `ftplib.FTP` or compatible classes to perform
most low-level FTP operations. In Python 3.8 and before, the default
encoding for FTP paths was latin-1, but there was no official
documentation on using a different encoding. In Python 3.9, the
default encoding changed to UTF-8 and the encoding is configurable
with an `ftplib.FTP` constructor argument.

The documentation of ftputil 4.0.0 and earlier stated:
- ftputil uses latin-1 encoding for paths
- ftputil uses `ftplib.FTP` as the default session factory

With the change of the default encoding in Python 3.9 these two
statements are contradictory. To resolve the conflict, the new
behavior of ftputil is:
- ftputil uses `ftplib.FTP` as default session factory, but explicitly
  sets the path encoding to latin-1 (regardless of the Python
  version). This is the same behavior as in ftputil 4.0.0 or earlier
  if running under Python 3.8 or earlier.
- If client code uses a custom session factory (i. e. the
  `session_factory` argument of the `FTPHost` constructor), ftputil
  will take the path encoding to use for `bytes` paths from the
  `encoding` attribute of an FTP session from this factory. If there's
  no such attribute, an exception is raised.

Other changes
~~~~~~~~~~~~~

`ftputil.session.session_factory` got a new keyword argument
`encoding` to set the path encoding of the sessions created by the
factory. If the argument isn't specified, the path encoding will be
taken from the `base_class` argument. (This means that the encoding
will be different for `ftplib.FTP` in Python 3.8 or earlier vs.
Python 3.9 or later.)

Documentation
-------------

The documentation for ftputil can be found in the file ftputil.txt
(reStructuredText format) or ftputil.html (recommended, generated from
ftputil.txt).

Prerequisites
-------------

To use ftputil, you need Python, at least version 3.6.

Installation
------------

*If you have an older version of ftputil installed, delete it or
move it somewhere else, so that it doesn't conflict with the new
version.*

You can install ftputil with pip:

  pip install ftputil

Unless you're installing ftputil in a virtual environment, you'll
probably need root/administrator privileges.

Note that ftputil versions with a different major version number won't
be fully backward-compatible with the previous version. Examples are
the changes from 2.8 to 3.0 and from 3.4 to 4.0.0.

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


[1] https://docs.python.org/3/whatsnew/3.9.html#changes-in-the-python-api
    "The encoding parameter has been added to the classes ftplib.FTP
    and ftplib.FTP_TLS as a keyword-only parameter, and the default
    encoding is changed from Latin-1 to UTF-8 to follow RFC 2640."
[2] https://ftputil.sschwarzer.net/trac/wiki/Documentation
[3] https://ftputil.sschwarzer.net/trac/ticket/143
