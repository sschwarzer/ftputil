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

This release fixes a regression in ftputil 5.0.0. [1]

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


[1] https://ftputil.sschwarzer.net/trac/ticket/145
