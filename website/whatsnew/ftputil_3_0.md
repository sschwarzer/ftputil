---
permalink: /whatsnew/ftputil_3_0
title: What's new in ftputil 3.0?
---

**Version:** 3.0\
**Date:** 2013-09-29\
**Author:** Stefan Schwarzer

## Added support for Python 3

This ftputil release adds support for Python 3.0 and up.

Python 2 and 3 are supported with the same source code. Also, the API
including the semantics is the same. As for Python 3 code, in ftputil
3.0 unicode is somewhat preferred over byte strings. On the other hand,
in line with the file system APIs of both Python 2 and 3, methods take
either byte strings or unicode strings. Methods that take and return
strings (for example, `FTPHost.path.abspath` or `FTPHost.listdir`),
return the same string type they get.

> **Note**
>
> Both Python 2 and 3 have two "string" types where one type represents a
> sequence of bytes and the other type character (text) data.
>
> | Python version | Binary type | Text type | Default string literal type |
> |----------------|-------------|-----------|-----------------------------|
> | 2              | `str`       | `unicode` | `str` (= binary type)       |
> | 3              | `bytes`     | `str`     | `str` (= text type)         |

So both lines of Python have an `str` type, but in Python 2 it's the
byte type and in Python 3 the text type. The `str` type is also what you
get when you write a literal string without any prefixes. For example
`"Python"` is a binary string in Python 2 and a text (unicode) string in
Python 3.

If this seems confusing, please read
[this description](https://docs.python.org/3.0/whatsnew/3.0.html#text-vs-data-instead-of-unicode-vs-8-bit)
in the Python documentation for more details.

## Dropped support for Python 2.4 and 2.5

To make it easier to use the same code for Python 2 and 3, I decided to
use the Python 3 features backported to Python 2.6. As a consequence,
ftputil 3.0 doesn't work with Python 2.4 and 2.5.

## Newlines and encoding of remote file content

Traditionally, "text mode" for FTP transfers meant translation to `\r\n`
newlines, even between transfers of Unix clients and Unix servers. Since
this presumably most of the time is neither the expected nor the desired
behavior, the `FTPHost.open` method now has the API and semantics of the
built-in `open` function in Python 3. If you want the same API for
*local* files in Python 2.6 and 2.7, you can use the `open` function
from the `io` module.

Thus, when opening remote files in *binary* mode, the new API does *not*
accept an encoding argument. On the other hand, opening a file in text
mode always implies an encoding step when writing and decoding step when
reading files. If the `encoding` argument isn't specified, it defaults
to the value of `locale.getpreferredencoding(False)`.

Also as with Python 3's `open` builtin, opening a file in binary mode
for reading will give you byte string data. If you write to a file
opened in binary mode, you must write byte strings. Along the same
lines, files opened in text mode will give you unicode strings when
read, and require unicode strings to be passed to write operations.

## Module and method name changes

In earlier ftputil versions, most module names had a redundant `ftp_`
prefix. In ftputil 3.0, these prefixes are removed. Of the module names
that are part of the public ftputil API, this affects only
`ftputil.error` and `ftputil.stat`.

In Python 2.2, `file` became an alias for `open`, and previous ftputil
versions also had an `FTPHost.file` besides the `FTPHost.open` method.
In Python 3.0, the `file` builtin was removed and the return values from
the built-in `open` methods are no longer `file` instances. Along the
same lines, ftputil 3.0 also drops the `FTPHost.file` alias and requires
`FTPHost.open`.

## Upload and download modes

The `FTPHost` methods for downloading and uploading files (`download`,
`download_if_newer`, `upload` and `upload_if_newer`) now always use
binary mode; a `mode` argument is no longer needed or even allowed.
Although this behavior makes downloads and uploads slightly less
flexible, it should cover almost all use cases.

If you *really* want to do a transfer involving files opened in text
mode, you can still do:
```python
import ftputil.file_transfer

...

with FTPHost.open("source.txt", "r", encoding="UTF-8") as source, \
     FTPHost.open("target.txt", "w", encoding="latin1") as target:
    ftputil.file_transfer.copyfileobj(source, target)
```

Note that it's not possible anymore to open one file in binary mode and
the other file in text mode and transfer data between them with
`copyfileobj`. For example, opening the source in binary mode will read
byte strings, but a target file opened in text mode will only allow
writing of unicode strings. Then again, I assume that the cases where
you want a mixed binary/text mode transfer should be *very* rare.

## Custom parsers receive lines as unicode strings

Custom parsers, as described in the
[documentation](https://ftputil.sschwarzer.net/documentation#writing-directory-parsers),
receive a text line for each directory entry in the methods
`ignores_line` and `parse_line`. In previous ftputil versions, the
`line` arguments were byte strings; now they're unicode strings.

If you aren't sure what this is about, this may help: If you never used
the `FTPHost.set_parser` method, you can ignore this section. :-)

## Porting to ftputil 3.0

-   It's likely that you catch an ftputil exception here and there. In
    that case, you need to change `import ftputil.ftp_error` to
    `import ftputil.error` and modify the uses of the module
    accordingly. If you used `from ftputil import ftp_error`, you can
    change this to `from ftputil import error as ftp_error` without
    changing the code using the module.
-   If you use the download or upload methods, you need to remove the
    `mode` argument from the call. If you used something else than `"b"`
    for binary mode (which I assume to be unlikely), you'll need to
    adapt the code that calls the download or upload methods.
-   If you use custom parsers, you'll need to change
    `import ftputil.ftp_stat` to `import ftputil.stat` and adapt your
    code in the module. Moreover, you might need to change your
    `ignores_line` or `parse_line` calls if they rely on their `line`
    argument being a byte string.
-   If you use remote files, especially ones opened in text mode, you
    may need to change your code to adapt to the changes in newline
    conversion, encoding and/or string type (see above sections).

> **Note**
>
> In the root directory of the installed ftputil package is a script
> `find_invalid_code.py` which, given a start directory as argument, will
> scan that directory tree for code that may need to be fixed. However,
> this script uses very simple heuristics, so it may miss some problematic
> code or list perfectly valid code.
>
> In particular, you may want to change the regular expression string
> `HOST_REGEX` for the names you usually use for `FTPHost` objects.

## Questions and answers

### The advice to "adapt code to the new string types" is rather vague. Can't you be more specific?

It's difficult to be more specific without knowing your application.

That said, best practices nowadays are:

-   If you're dealing with character data, use unicode strings whenever
    possible. In Python 2, this means the `unicode` type and in Python 3
    the `str` type.
-   Whenever you deal with binary data which is actually character data,
    decode it as *soon* as possible when *reading* data. Encode the data
    as *late* as possible when *writing* data.

Yes, I know that's not much more specific.

### Why don't you use a "Python 2 API" for Python 2 and a "Python 3 API" for Python 3?

(What's meant here is, for example, that if you opened a remote file as
text, the read data could be of byte string type in Python 2 and of
unicode type in Python 3. Similarly, under Python 2 a text file opened
for writing could accept both byte strings and unicode strings in the
`write*` methods.)

Actually, I had at first thought of implementing this but dropped the
idea because it has several problems:

-   Basically, I would have to support two APIs for the same set of
    methods. I can imagine that some things can be simplified by just
    using `str` to convert to the "right" string type automatically, but
    I assume these opportunities would be rather the exception than the
    rule. I'd certainly not look forward to maintaining such code.
-   Using two different APIs might require people to change their code
    if they move from using ftputil 3.x in Python 2 to using it in
    Python 3.
-   Developers who want to support both Python 2 and 3 with the same
    source code (as I do now in ftputil) would "inherit" the "dual API"
    and would have to use different wrapper code depending on the Python
    version their code is run under.

For these reasons, I [ended
up](https://groups.google.com/forum/?fromgroups=#!topic/comp.lang.python/XKof6DpNyH4)
choosing the same API semantics for Python 2 and 3.

### Why don't you use the [six](https://pypi.python.org/pypi/six/) module to be able to support Python 2.4 and 2.5?

There are two reasons:

-   ftputil so far has no dependencies other than the Python standard
    library, and I think that's a nice feature.
-   Although `six` makes it easier to support Python 2.4/2.5 and Python
    3 at the same time, the resulting code is somewhat awkward. I wanted
    a code base that feels more like "modern Python"; I wanted to use
    the Python 3 features backported to Python 2.6 and 2.7.

### Why don't you use [2to3](https://docs.python.org/2/library/2to3.html) to generate the Python 3 version of ftputil?

I had considered this when I started adapting the ftputil source code
for Python 3. On the other hand, although using 2to3 used to be the
recommended approach for Python 3 support, even [rather large
projects](https://docs.djangoproject.com/en/dev/topics/python3/) have
chosen the route of having one code base and using it unmodified for
Python 2 and 3.

When I looked into this approach for ftputil 3.0, it became quickly
obvious that it would be easier and I found it worked out very well.
