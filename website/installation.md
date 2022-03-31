---
permalink: /installation
title: Installation and versions
---

## Python package index (PyPI)

The usual way to install ftputil is with pip:
```bash
python3 -m pip install ftputil
```

Of course, you can also use any other tool that can install packages
from the [Python Package Index](https://pypi.python.org/).

## Conda

If you prefer Conda, you can install ftputil from the `conda-forge`
channel:
```bash
conda install -c conda-forge ftputil
```

## Backward compatibility

ftputil follows [semantic versioning](https://semver.org/). This means
only changes in the first part of the version number break backward
compatibility.

Even if a version of ftputil breaks backward compatibility, I try to
limit the effects, so you may not be affected. Check the release
announcements on the [mailing
list]({{ site.data.urls.mailing_list }}) for details of new
backward-incompatible versions before making a version switch. Here
are
[two](https://lists.sr.ht/~sschwarzer/ftputil/%3C29e84e80-a3dc-6508-f46f-d517a4192926%40sschwarzer.net%3E)
[examples](https://lists.sr.ht/~sschwarzer/ftputil/%3Cdf64c8ed-2a03-be3d-6bb0-236fc85c90a9%40sschwarzer.net%3E).
If you're unsure how a new version might affect you, please ask on the
[mailing list]({{ site.data.urls.mailing_list }}).

## Version history

| Version | Status | Release date | Main changes to previous version |
|---------|--------|--------------|----------------------------------|
| 5.0.3 | **Current stable release** | 2022-01-26 | Fix potential data loss for FTPS ([#149](https://todo.sr.ht/~ssschwarzer/ftputil/149)) |
| 5.0.2 |  | 2021-11-13 | Fix handling of empty paths ([#148](https://todo.sr.ht/~ssschwarzer/ftputil/148)) |
| 5.0.1 |  | 2021-03-18 | Fix regression for default session factory ([#145](https://todo.sr.ht/~ssschwarzer/ftputil/145)) |
| 5.0.0 |  | 2021-02-17 | Resolve Python 3.9 ftplib compatibility problem ([#143](https://todo.sr.ht/~ssschwarzer/ftputil/143)) <br> **Note: This version is not backward-compatible with ftputil 4.0.0 and earlier.** |
| 4.0.0 |  | 2020-06-13 | Support path-like objects ([#119](https://todo.sr.ht/~ssschwarzer/ftputil/119)), changed time shift handling ([#134](https://todo.sr.ht/~ssschwarzer/ftputil/134)), support `exist_ok` ([#117](https://todo.sr.ht/~ssschwarzer/ftputil/117)), bugfix ([#136](https://todo.sr.ht/~ssschwarzer/ftputil/136)) <br> **Note: This version is not backward-compatible with ftputil 3.4 and earlier.** |
| 3.4 | Last version with support for Python < 3.6 | 2017-11-08 | Bugfixes ([#107](https://todo.sr.ht/~ssschwarzer/ftputil/107), [#109](https://todo.sr.ht/~ssschwarzer/ftputil/109), [#112](https://todo.sr.ht/~ssschwarzer/ftputil/112), [#113](https://todo.sr.ht/~ssschwarzer/ftputil/113), [#114](https://todo.sr.ht/~ssschwarzer/ftputil/114)), add deprecation warnings |
| 3.3.1 | | 2016-02-18 | Handle delayed 226 reply under high load ([#102](https://todo.sr.ht/~ssschwarzer/ftputil/102)) |
| 3.3 | | 2015-12-25 | `rest` argument for `FTPHost.open` ([#61](https://todo.sr.ht/~ssschwarzer/ftputil/61)), fixed non-ASCII paths under Python 2 ([#100](https://todo.sr.ht/~ssschwarzer/ftputil/100)), `makedirs` for virtual directories ([#86](https://todo.sr.ht/~ssschwarzer/ftputil/86)), small improvements ([#89](https://todo.sr.ht/~ssschwarzer/ftputil/89), [#91](https://todo.sr.ht/~ssschwarzer/ftputil/91), [#92](https://todo.sr.ht/~ssschwarzer/ftputil/92)) |
| 3.2 | | 2014-10-12 | Extracted SocketFileAdapter module for use in other projects, more robust datetime parsing ([#83](https://todo.sr.ht/~ssschwarzer/ftputil/83), [#85](https://todo.sr.ht/~ssschwarzer/ftputil/85)) |
| 3.1 | | 2014-06-16 | Generic session factory, `followlinks` in `FTPHost.walk`, bugfixes ([#76](https://todo.sr.ht/~ssschwarzer/ftputil/76), [#77](https://todo.sr.ht/~ssschwarzer/ftputil/77), [#78](https://todo.sr.ht/~ssschwarzer/ftputil/78), [#81](https://todo.sr.ht/~ssschwarzer/ftputil/81)) |
| 3.0 | | 2013-11-17 | Support for Python 3.0, changed API for Python 2.x, support for Python 2.4/2.5 removed. <br> **Note: This version is *not* backward-compatible with ftputil 2.8 and earlier.** |
| 2.8 | Last version with Python 2.4/2.5 support | 2013-03-30 | Use `LIST -a` by default, bugfixes ([#39](https://todo.sr.ht/~ssschwarzer/ftputil/39), [#65](https://todo.sr.ht/~ssschwarzer/ftputil/65), [#66](https://todo.sr.ht/~ssschwarzer/ftputil/66), [#67](https://todo.sr.ht/~ssschwarzer/ftputil/67), [#69](https://todo.sr.ht/~ssschwarzer/ftputil/69)) |
| 2.7.1 | | 2012-07-14 | Packaging fix ([#64](https://todo.sr.ht/~ssschwarzer/ftputil/64)) |
| 2.7 | | 2012-07-08 | Try to list "hidden" items by default ([#23](https://todo.sr.ht/~ssschwarzer/ftputil/23)), bugfix ([#62](https://todo.sr.ht/~ssschwarzer/ftputil/62)) |
| 2.6 | | 2011-03-12 | Cache improvements, bugfixes ([#53](https://todo.sr.ht/~ssschwarzer/ftputil/53), [#55](https://todo.sr.ht/~ssschwarzer/ftputil/55), [#56](https://todo.sr.ht/~ssschwarzer/ftputil/56)) |
| 2.5 | | 2010-10-24 | Upload/download callbacks, bugfixes ([#44](https://todo.sr.ht/~ssschwarzer/ftputil/44), [#46](https://todo.sr.ht/~ssschwarzer/ftputil/46), [#47](https://todo.sr.ht/~ssschwarzer/ftputil/47), [#51](https://todo.sr.ht/~ssschwarzer/ftputil/51)) |
| 2.4.2 | Last version with Python 2.3 support | 2009-11-12 | Bugfixes ([#33](https://todo.sr.ht/~ssschwarzer/ftputil/33), [#35](https://todo.sr.ht/~ssschwarzer/ftputil/35), [#38](https://todo.sr.ht/~ssschwarzer/ftputil/38), [#41](https://todo.sr.ht/~ssschwarzer/ftputil/41)) |
| 2.4.1 | | 2009-05-10 | Bugfixes ([#32](https://todo.sr.ht/~ssschwarzer/ftputil/32), [#36](https://todo.sr.ht/~ssschwarzer/ftputil/36), [#37](https://todo.sr.ht/~ssschwarzer/ftputil/37)) |
| 2.4 | | 2009-02-15 | `chmod` method for remote dirs/files |
| 2.3 | | 2008-09-06 | Support for `with` statement |
| 2.2.4 | | 2008-08-30 | Bugfix: relative directories by makedirs on Windows ([#27](https://todo.sr.ht/~ssschwarzer/ftputil/27)) |
| 2.2.3 | | 2007-07-22 | Bugfix: makedirs works from non-root directory ([#22](https://todo.sr.ht/~ssschwarzer/ftputil/22)) |
| 2.2.2 | | 2007-04-22 | Bugfix: handle whitespace in path names more reliably (see [#11](https://todo.sr.ht/~ssschwarzer/ftputil/11)) |
| 2.2.1 | | 2007-01-26 | Bugfix: catch status code 451 when closing FTPFiles (see [#17](https://todo.sr.ht/~ssschwarzer/ftputil/17)) |
| 2.2 |  | 2006-12-24 | Caching of stat results; iterator protocol for FTP files; interface for custom parsers   |
| 2.1.1 | | 2006-08-19 | Bugfix: handle certain status codes more gracefully ([#17](https://todo.sr.ht/~ssschwarzer/ftputil/17)) |
| 2.1 | | 2006-03-30 | See [announcement](https://lists.sr.ht/~sschwarzer/ftputil/%3C442C4F04.90002%40sschwarzer.net%3E) |
| 2.0.3 | | 2004-07-29 | Bugfix for inaccessible login directory |
| 2.0.2 | | 2004-04-18 | Included MANIFEST file |
