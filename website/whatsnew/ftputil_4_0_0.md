---
permalink: /whatsnew/ftputil_4_0_0
title: What's new in ftputil 4.0.0?
---

**Version:** 4.0.0\
**Date:** 2020-06-13\
**Author:** Stefan Schwarzer

## Supported Python versions

Support for Python 2 is dropped. The minimum required Python 3 version
is 3.6.

Find more details in [Questions and answers](#questions-and-answers).

## Path-like objects

Methods that take directory and file names as `str` or `bytes` objects
now also accept [path-like
objects](https://docs.python.org/3/library/os.html#os.PathLike).

## Time shift handling

ftputil uses the notion of "time shift" to deal with time zone
differences between client and server. This is important for the methods
`upload_if_newer` and `download_if_newer`.

The defintion of "time shift" changed from earlier ftputil versions to
ftputil 4.0.0.

Previously, the time shift was defined as

*time_used_by_server – local_time_used_by_client*

The new definition is

*time_used_by_server – [UTC](https://en.wikipedia.org/wiki/Coordinated_Universal_Time)*

Both definitions have their pros and cons (detailed in the [Questions
and answers](#questions-and-answers)).

### Porting

If you don't use any methods that deal with time stamps from the FTP
server, you can ignore the time shift redefinition. The affected methods
are `upload_if_newer`, `download_if_newer` and using the timestamp
values from the `stat` and `lstat` methods.

Ideally, you have write access on the server in the current directory.
In this case you can call `synchronize_times`:
```python
with ftputil.FTPHost(host, user, password) as ftp_host:
    ftp_host.synchronize_times()
    ...
```

If using `synchronize_times` isn't an option, you have to set the time
shift explicitly with `set_time_shift`:
```python
with ftputil.FTPHost(host, user, password) as ftp_host:
    ftp_host.set_time_shift(new_time_shift)
    ...
```

*If* you're sure the server in its directory listings uses the same
timezone as the client, you can use
```python
with ftputil.FTPHost(host, user, password) as ftp_host:
    ftp_host.set_time_shift(
      round((datetime.datetime.now() - datetime.datetime.utcnow()).seconds, -2)
    )
    ...
```

This is roughly equivalent to the old ftputil behavior. The only
difference is that the new behavior requires that you adapt the time
shift value if there's a switch to or from daylight saving time.

If you want to cover such daylight saving time switches as well, you
could override `time_shift()` to return the above value. This will
automatically adapt to daylight saving time switches because
`datetime.datetime.now()` will return the time for the changed UTC
offset. That said, I think this approach is a hack because it means that
calls to `set_time_shift` will effectively be ignored. So don't take
this approach as a recommendation.

You can use [this
script](https://ftputil.sschwarzer.net/trac/browser/find_problematic_code.py?format=txt)
to scan your code for uses of `time_shift()` or `set_time_shift`.
However, if you implicitly relied on the old default behavior (time
shift is 0.0 if client and server use the same time zone), you'll need
additional calls for `set_time_shift`.

## ftputil no longer uses the `-a` option by default

Earlier ftputil versions by default sent an `-a` option with the FTP
`DIR` command to include "hidden" directories and files (names starting
with a dot) in the listing.

That led to problems when the server [didn't understand the
option](https://ftputil.sschwarzer.net/trac/ticket/110) and treated it
as a directory or file name.

Therefore, ftputil no longer uses the `-a` option by default.

### Porting

You can enable the old behavior by setting `use_list_a_option` on the
`FTPHost` instance to `True`:
```python
with ftputil.FTPHost(host, user, password) as ftp_host:
    ftp_host.use_list_a_option = True
    ...
```

However, do this only if you're *sure* the server interprets the option
correctly!

## `makedirs` behaves as in Python 3

In Python 2, `os.makedirs` didn't complain if any directory in the path
to create already existed. Since ftputil was originally based on Python
2 behavior, this *was* also the behavior in `FTPHost.makedirs`.

Python 3 added an optional argument `exist_ok` with the default `False`.
With this default, `os.makedirs` raises an exception if any directory
but the last in the `path` argument exists.

Since Python 2 is used less and less, ftputil 4.0.0 follows the Python 3
semantics.

### Porting

If you want the old behavior of `FTPHost.makedirs`, pass
`exist_ok=True`. Note that there's also an unused `mode` argument for
consistency with the `os.makedirs` API, so make sure you pass `exist_ok`
as a keyword argument.

You can use [this
script](https://ftputil.sschwarzer.net/trac/browser/find_problematic_code.py?format=txt)
to scan your code for uses of `makedirs()`.

## Questions and answers

### Why is Python 2 no longer supported?

Since the start of the year Python 2 officially is no longer maintained
and supporting it in combination with Python 3 led to lots of extra
work. Therefore, I decided to drop support for Python 2.

### Why is the minimum version Python 3.6?

Python 3.4 and older versions are no longer supported by the CPython
team.

My plan *was* to support Python 3.5 since it's not yet end-of-life'd and
it may still be used in some LTS Linux/Unix distributions. However,
dropping Python 3.5 support made it much easier to implement [ticket
#119](https://ftputil.sschwarzer.net/trac/ticket/119), support for
[path-like
objects](https://docs.python.org/3/library/os.html#os.PathLike). Python
3.6 introduced some infrastructure so that code that used to use only
`str` and `bytes` paths can now use path-like objects as well. I
considered it more important to support path-like objects than Python
3.5. I guess it might have been possible to add support for path-like
objects on top of Python 3.5, but it would have been a hassle and Python
3.5 support officially ends in [just a few
months](https://devguide.python.org/#status-of-python-branches).

### Why a new time shift definition?

Both the old and the new approach have their pros and cons:

Regarding the old approach:

-   Pro: *If* the server uses the time zone of the client in directory
    listings, the default time shift of 0.0 will do the right thing.

-   Con: Since the time shift depends on *two* time zones, it's more
    difficult to reason about the (ftputil) code and write correct code.
    In the past, there have been multiple bugs in the time zone / time
    shift handling in ftputil, some of them occuring only under
    "interesting" conditions (around daylight saving time changes or
    year changes).

    Actually, I decided to implement the new approach when I ran into a
    bug around the last new year change.

Regarding the new approach:

-   Pro: The new behavior works better when the server is set to UTC.
    This is a sane setting because it avoids that an hour interval is
    used twice when there's a switch from daylight saving time to
    "normal" time. There are even more subtle problems with daylight
    saving time switches.
-   Pro: Since the time shift calculation depends on only one time zone
    (that of the server), the code in ftputil is easier to reason about
    and now hopefully more robust.
-   Con: The new approach is backward-incompatible, so users may have to
    adapt their code.
-   Con: *If* the server uses the time zone of the client in directory
    listings, the time shift must be adjusted whenever there's a switch
    to or from daylight saving time.

Neither of the two approaches is foolproof. For example, timestamps that
are older than the last daylight saving time switch may be calculated
wrongly because they may use a different time zone than the one
currently set by `set_time_shift`.
