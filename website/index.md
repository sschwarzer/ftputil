---
layout: default
permalink: /
title: ftputil — a high-level FTP client library for Python
---

The ftputil [Python](http://www.python.org) library is a high-level interface to
the [ftplib](https://docs.python.org/lib/module-ftplib.html) module. The FTPHost
objects generated with ftputil allow many operations similar to those of
[os](https://docs.python.org/lib/module-os.html),
[os.path](https://docs.python.org/lib/module-os.path.html) and
[shutil](https://docs.python.org/3/library/shutil.html).

Here are two examples:

```python
#!python
# Download some files from the login directory.
with ftputil.FTPHost('ftp.domain.com', 'user', 'secret') as host:
    names = host.listdir(host.curdir)
    for name in names:
        if host.path.isfile(name):
            # Remote name, local name
            host.download(name, name)

# Check if a remote text file contains "ftputil".
# Stop reading as soon as the string is found.
with host.file("some_file") as remote_fobj:
    for line in remote_fobj:
        if "ftputil" in line:
            found = True
            break
    else:
        found = False
```

See the [documentation](/documentation) for all the features.
