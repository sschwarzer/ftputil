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

Since version 2.7.1 the following changed:

- After some discussion [1] I decided to remove the auto-probing
  before using the `-a` option for `LIST` [2]. The option is used by
  default now, without probing for exceptions. If this new approach
  causes problems, you can use

    ftp_host = ftputil.FTPHost(...)
    ftp_host.use_list_a_option = False

- Several bugs were fixed. [3]

- The mailing lists have moved to

    ftputil@lists.sschwarzer.net
    ftputil-tickets@lists.sschwarzer.net

  The first list requires a subscription before you can post. The
  second list is read-only anway.

  Thanks to Codespeak.net for having hosted the lists for almost
  ten years. :-)

Documentation
-------------

The documentation for ftputil can be found in the file ftputil.txt
(reStructuredText format) or ftputil.html (recommended, generated from
ftputil.txt).

Prerequisites
-------------

To use ftputil, you need Python, at least version 2.4. Python is a
programming language, available from http://www.python.org for free.

Installation
------------

- *If you have an older version of ftputil installed, delete it or
  move it somewhere else, so that it doesn't conflict with the new
  version!*

- Unpack the archive file containing the distribution files. If you
  had an ftputil version 2.6, you would type at the shell prompt:

    tar xzf ftputil-2.6.tar.gz

  However, if you read this, you probably unpacked the archive
  already. ;-)

- Make the directory to where the files were unpacked your current
  directory. Assume that after unpacking, you have a directory
  ftputil-2.6. Make it the current directory with

    cd ftputil-2.6

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
http://www.opensource.org/licenses/bsd-license.html ).

Authors
-------

Stefan Schwarzer <sschwarzer@sschwarzer.net>

Evan Prodromou <evan@bad.dynu.ca> (lrucache module)

Please provide feedback! It's certainly appreciated. :-)


[1] http://ftputil.sschwarzer.net/trac/ticket/65
[2] http://lists.sschwarzer.net/pipermail/ftputil/2012q3/000350.html
[3] http://ftputil.sschwarzer.net/trac/ticket/39
    http://ftputil.sschwarzer.net/trac/ticket/65
    http://ftputil.sschwarzer.net/trac/ticket/66
    http://ftputil.sschwarzer.net/trac/ticket/67
    http://ftputil.sschwarzer.net/trac/ticket/69
