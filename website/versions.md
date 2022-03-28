---
layout: default
permalink: /versions
title: Version history
---

# Version history

*If you came here via an external link and don't know about ftputil,
go to the [homepage](/).*

**The recommended way to install ftputil is with pip:**
```bash
python3 -m pip install ftputil
```

| Version | Status | Release date | Main changes to previous version |
|---------|--------|--------------|----------------------------------|
| 5.0.3 | **current stable release** | 2022-01-26 | Fix potential data loss for FTPS (#149) |
| 5.0.2 |  | 2021-11-13 | Fix handling of empty paths (#148) |
| 5.0.1 |  | 2021-03-18 | Fix regression for default session factory (#145) |
| 5.0.0 |  | 2021-02-17 | Resolve Python 3.9 ftplib compatibility problem (#143) <br> **Note: This version is not backward-compatible with ftputil 4.0.0 and earlier.** |
| 4.0.0 |  | 2020-06-13 | support path-like objects (#119), changed time shift handling (#134), support `exist_ok` (#117), bugfix (#136) <br> **Note: This version is not backward-compatible with ftputil 3.4 and earlier.** |
| 3.4 | last version with support for Python < 3.6 | 2017-11-08 | bugfixes (#107, #109, #112, #113, #114), add deprecation warnings |
| 3.3.1 | | 2016-02-18 | handle delayed 226 reply under high load (#102) |
| 3.3 | | 2015-12-25 | `rest` argument for `FTPHost.open` (#61), fixed non-ASCII paths under Python 2 (#100), `makedirs` for virtual directories (#86), small improvements (#89, #91, #92) |
| 3.2 | | 2014-10-12 | extracted SocketFileAdapter module for use in other projects, more robust datetime parsing (#83, #85) |
| 3.1 | | 2014-06-16 | Generic session factory, `followlinks` in `FTPHost.walk`, bugfixes (#76, #77, #78, #81) |
| 3.0 | | 2013-11-17 | Support for Python 3.0, changed API for Python 2.x, support for Python 2.4/2.5 removed. <br> **Note: This version is *not* backward-compatible with ftputil 2.8 and earlier.** |
| 2.8 | last version with Python 2.4/2.5 support | 2013-03-30 | use `LIST -a` by default, bugfixes (#39, #65, #66, #67, #69) |
| 2.7.1 | | 2012-07-14 | packaging fix (#64) |
| 2.7 | | 2012-07-08 | try to list "hidden" items by default (#23), bugfix (#62) |
| 2.6 | | 2011-03-12 | cache improvements, bugfixes (#53, #55, #56) |
| 2.5 | | 2010-10-24 | upload/download callbacks, bugfixes (#44, #46, #47, #51) |
| 2.4.2 | last version with Python 2.3 support | 2009-11-12 | bugfixes (#33, #35, #38, #41) |
| 2.4.1 | | 2009-05-10 | bugfixes (#32, #36, #37) |
| 2.4 | | 2009-02-15 | `chmod` method for remote dirs/files |
| 2.3 | | 2008-09-06 | support for `with` statement |
| 2.2.4 | | 2008-08-30 | bugfix: relative directories by makedirs on Windows (#27) |
| 2.2.3 | | 2007-07-22 | bugfix: makedirs works from non-root directory (#22) |
| 2.2.2 | | 2007-04-22 | bugfix: handle whitespace in path names more reliably (see #11) |
| 2.2.1 | | 2007-01-26 | bugfix: catch status code 451 when closing FTPFiles (see #17) |
| 2.2 |  | 2006-12-24 | caching of stat results; iterator protocol for FTP files; interface for custom parsers   |
| 2.1.1 | | 2006-08-19 | bugfix: handle certain status codes more gracefully (#17) |
| 2.1 | | 2006-03-30 | see [announcement](https://lists.sr.ht/~sschwarzer/ftputil/%3C442C4F04.90002%40sschwarzer.net%3E) |
| 2.0.3 | | 2004-07-29 | bugfix for inaccessible login directory |
| 2.0.2 | | 2004-04-18 | included MANIFEST file |
