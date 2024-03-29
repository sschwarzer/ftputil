---
permalink: /documentation
title: Documentation
---

**Version:** 5.1.0\
**Date:** 2024-01-06\
**Keywords:** FTP, `ftplib` substitute, virtual filesystem, pure Python\
**Author:** Stefan Schwarzer


## Introduction

The `ftputil` module is a high-level interface to the
[ftplib](https://docs.python.org/library/ftplib.html) module. The
[FTPHost objects](#ftphost-objects) generated from it allow many
operations similar to those of
[os](https://docs.python.org/library/os.html),
[os.path](https://docs.python.org/library/os.path.html) and
[shutil](https://docs.python.org/library/shutil.html).

### Code examples

```python
import ftputil

# Download some files from the login directory.
with ftputil.FTPHost("ftp.domain.com", "user", "password") as ftp_host:
names = ftp_host.listdir(ftp_host.curdir)
for name in names:
    if ftp_host.path.isfile(name):
        ftp_host.download(name, name)  # remote, local

# Make a new directory and copy a remote file into it.
ftp_host.mkdir("newdir")
with ftp_host.open("index.html", "rb") as source:
    with ftp_host.open("newdir/index.html", "wb") as target:
        ftp_host.copyfileobj(source, target)  # similar to shutil.copyfileobj
```

Also, there are [FTPHost.lstat](#FTPHost.lstat) and
[FTPHost.stat](#FTPHost.stat) to request size and modification time of a
file. The latter can also follow links, similar to
[os.stat](https://docs.python.org/library/os.html#os.stat).
[FTPHost.walk](#FTPHost.walk) and
[FTPHost.path.walk](#FTPHost.path.walk) work, too.

### Features

-   Method names are familiar from Python's `os`, `os.path` and `shutil`
    modules. For example, use `os.path.join` to join paths for a local
    file system and `ftp_host.path.join` to join paths for a remote FTP
    file system.
-   Remote file system navigation (`getcwd`, `chdir`)
-   Upload and download files (`upload`, `upload_if_newer`, `download`,
    `download_if_newer`)
-   Time zone synchronization between client and server (needed for
    `upload_if_newer` and `download_if_newer`)
-   Create and remove directories (`mkdir`, `makedirs`, `rmdir`,
    `rmtree`) and remove files (`remove`)
-   Get information about directories, files and links (`listdir`,
    `stat`, `lstat`, `exists`, `isdir`, `isfile`, `islink`, `abspath`,
    `dirname`, `basename` etc.)
-   Iterate over remote file systems (`walk`)
-   Local caching of results from `lstat` and `stat` calls to reduce
    network access (also applies to `exists`, `getmtime` etc.).
-   Read files from and write files to remote hosts via file-like
    objects (`FTPHost.open`); the generated file-like objects have the
    familiar methods like `read`, `readline`, `readlines`, `write`,
    `writelines` and `close`. You can also iterate over these files line
    by line in a `for` loop.

## Exception hierarchy

The exceptions are in the namespace of the `ftputil.error` module, e.g.
`ftputil.error.TemporaryError`.

The exception classes are organized as follows:

```plaintext
FTPError
FTPOSError(FTPError, OSError)
    PermanentError(FTPOSError)
        CommandNotImplementedError(PermanentError)
    TemporaryError(FTPOSError)
FTPIOError(FTPError)
InternalError(FTPError)
    InaccessibleLoginDirError(InternalError)
    NoEncodingError(InternalError)
    ParserError(InternalError)
    RootDirError(InternalError)
    TimeShiftError(InternalError)
```

and are described here:

-   `FTPError`

    is the root of the exception hierarchy of the module.

-   `FTPOSError`

    is derived from `OSError`. This is for similarity between the os
    module and `FTPHost` objects. Compare
    ```python
    try:
        os.chdir("nonexisting_directory")
    except OSError:
        ...
    ```
    with
    ```python
    host = ftputil.FTPHost("host", "user", "password")
    try:
        host.chdir("nonexisting_directory")
    except OSError:
        ...
    ```

    Imagine a function
    ```python
    def func(path, file):
        ...
    ```
    which works on the local file system and catches `OSErrors`. If you
    change the parameter list to
    ```python
    def func(path, file, os=os):
        ...
    ```
    where `os` denotes the `os` module, you can call the function also
    as
    ```python
    host = ftputil.FTPHost("host", "user", "password")
    func(path, file, os=host)
    ```
    to use the same code for both a local and remote file system.
    Another similarity between `OSError` and `FTPOSError` is that the
    latter holds the FTP server return code in the `errno` attribute of
    the exception object and the error text in `strerror`.

-   `PermanentError`

    is raised for 5xx return codes from the FTP server. This corresponds
    to `ftplib.error_perm` (though `PermanentError` and
    `ftplib.error_perm` are *not* identical).

-   `CommandNotImplementedError`

    indicates that an underlying command the code tries to use is not
    implemented. For an example, see the description of the
    [FTPHost.chmod](#FTPHost.chmod) method.

-   `TemporaryError`

    is raised for FTP return codes from the 4xx category. This
    corresponds to `ftplib.error_temp` (though `TemporaryError` and
    `ftplib.error_temp` are *not* identical).

-   `FTPIOError`

    denotes an I/O error on the remote host. This appears mainly with
    file-like objects that are retrieved by calling `FTPHost.open`.
    Compare
    ```python
    >>> try:
    ...     f = open("not_there")
    ... except IOError as obj:
    ...     print(obj.errno)
    ...     print(obj.strerror)
    ...
    2
    No such file or directory
    ```
    with
    ```python
    >>> ftp_host = ftputil.FTPHost("host", "user", "password")
    >>> try:
    ...     f = ftp_host.open("not_there")
    ... except IOError as obj:
    ...     print(obj.errno)
    ...     print(obj.strerror)
    ...
    550
    550 not_there: No such file or directory.
    ```

    As you can see, both code snippets are similar. However, the error
    codes aren't the same.

-   `InternalError`

    subsumes exception classes for signaling errors due to limitations
    of the FTP protocol or the concrete implementation of `ftputil`.

-   `InaccessibleLoginDirError`

    This exception is raised if the directory in which "you" are placed
    upon login is not accessible, i.e. a `chdir` call with the
    directory as argument would fail.

-   `NoEncodingError`

    is raised if an FTP session instance doesn't have an `encoding`
    attribute (see also [session factories](#session-factories)).

-   `ParserError`

    is used for errors during the parsing of directory listings from the
    server. This exception is used by the `FTPHost` methods `stat`,
    `lstat`, and `listdir`.

-   `RootDirError`

    Because of the implementation of the `lstat` method it is not
    possible to do a `stat` call on the root directory `/`. If you know
    *any* way to do it, please let me know. :-)

    This problem does *not* affect stat calls on items *in* the root
    directory.

-   `TimeShiftError`

    is used to denote errors which relate to setting the [time
    shift](#time shift).

## `FTPHost` objects

### Construction

#### Introduction

`FTPHost` instances can be created with the following call:
```python
ftp_host = ftputil.FTPHost(server, user, password, account,
                           session_factory=ftplib.FTP)
```

The first four parameters are strings with the same meaning as for the
FTP class in the `ftplib` module. Usually the `account` and
`session_factory` arguments aren't needed though.

`FTPHost` objects can also be used in a `with` statement:
```python
import ftputil

with ftputil.FTPHost(server, user, password) as ftp_host:
    print(ftp_host.listdir(ftp_host.curdir))
```

After the `with` block, the `FTPHost` instance and the associated FTP
sessions will be closed automatically.

If something goes wrong during the `FTPHost` construction or in the body
of the `with` statement, the instance is closed as well. Exceptions in
the `with` block will be propagated.

#### Session factories

The keyword argument `session_factory` may be used to generate FTP
connections with other factories than the default `ftplib.FTP`. For
example, the standard library contains a class `ftplib.FTP_TLS` which extends
`ftplib.FTP` to use an encrypted connection.

In fact, all positional and keyword arguments other than
`session_factory` are passed to the factory to generate a new background
session. This also happens for every remote file that is opened; see
below.

This functionality of the constructor also allows to wrap `ftplib.FTP`
objects to do something that wouldn't be possible with the `ftplib.FTP`
constructor alone.

As an example, assume you want to connect to another than the default
port, but `ftplib.FTP` only offers this by means of its `connect`
method, not via its constructor. One solution is to use a custom class
as a session factory:
```python
import ftplib
import ftputil

EXAMPLE_PORT = 50001

class MySession(ftplib.FTP):

    def __init__(self, host, userid, password, port):
        """Act like ftplib.FTP's constructor but connect to another port."""
        ftplib.FTP.__init__(self)
        self.connect(host, port)
        self.login(userid, password)

# Do _not_ use an _instance_ of `MySession()` as factory, -
# use the class itself.
with ftputil.FTPHost(host, userid, password, port=EXAMPLE_PORT,
                     session_factory=MySession) as ftp_host:
    # Use `ftp_host` as usual.
    ...
```

On login, the format of the directory listings (needed for stat'ing
files and directories) should be determined automatically. If not,
please [enter a ticket]({{ site.data.urls.tracker }}).

For the most common uses you don't need to create your own session
factory class though. The `ftputil.session` module has a function
`session_factory` that can create session factories for a variety of
parameters:
```python
session_factory(base_class=ftplib.FTP,
                port=21,
                use_passive_mode=None,
                encrypt_data_channel=True,
                encoding=None,
                debug_level=None)
```
with

-   `base_class` is a base class to inherit a new session factory class
    from. By default, this is `ftplib.FTP` from the Python standard
    library.

-   `port` is the command channel port. The default is 21, used in most
    FTP server configurations.

-   `use_passive_mode` is either a boolean that determines whether
    passive mode should be used or `None`. `None` means to let the base
    class choose active or passive mode.

-   `encrypt_data_channel` defines whether to encrypt the data channel
    for secure connections. This is only supported for the base classes
    `ftplib.FTP_TLS` and `M2Crypto.ftpslib.FTP_TLS`, otherwise the
    parameter is ignored.

-   `encoding` can be a string to set the encoding of directory and
    file _paths_ on the remote server. (This has nothing to do with
    the encoding of file _contents_!) If you pass a string and your
    base class is neither `ftplib.FTP` nor `ftplib.FTP_TLS`, the used
    heuristic in `session_factory` may not work reliably. Therefore,
    if in doubt, let `encoding` be `None` and define your `base_class`
    so that it sets the encoding you want.

    **Note:** In Python 3.9, the default path encoding for
    `ftplib.FTP` and `ftplib.FTP_TLS` changed from previously
    "latin-1" to "utf-8". Hence, if you don't pass an `encoding` to
    `session_factory`, you'll get different path encodings for Python
    3.8 and earlier vs. Python 3.9 and later.

    If you're sure that you always use only ASCII characters in your
    remote paths, you don't need to worry about the path encoding and
    don't need to use the `encoding` argument.

-   `debug_level` sets the debug level for FTP session instances. The
    semantics is defined by the base class. For example, a debug level
    of 2 causes the most verbose output for Python's `ftplib.FTP` class.

All of these parameters can be combined. For example, you could use
```python
import ftplib

import ftputil
import ftputil.session


my_session_factory = ftputil.session.session_factory(
                       base_class=ftpslib.FTP_TLS,
                       port=31,
                       encrypt_data_channel=True,
                       encoding="UTF-8",
                       debug_level=2)

with ftputil.FTPHost(server, user, password,
                     session_factory=my_session_factory) as ftp_host:
    ...
```
to create and use a session factory derived from `ftplib.FTP_TLS` that
connects on command channel 31, will encrypt the data channel, use the
UTF-8 encoding for remote paths and print output for debug level 2.

> **Note**
>
> Generally, you can achieve everything you can do with
`ftputil.session.session_factory` with an explicit session factory as
described at the start of this section.

### Directory and file names

> **Note**
>
> Keep in mind that this section only applies to directory and file
*names*, not file *contents*. Encoding and decoding for file contents is
handled by the `encoding` argument for [FTPHost.open](#FTPHost.open).

Generally, paths can be `str` or `bytes` objects (or
[PathLike](https://docs.python.org/3/library/os.html#os.PathLike)
objects wrapping `str` or `bytes`). However, you can't mix different
string types (`bytes` and `str`) in one call (for example in
`FTPHost.path.join`). If a method gets a string argument (or a string
argument wrapped in a
[PathLike](https://docs.python.org/3/library/os.html#os.PathLike)
object) and returns one or more strings, these strings will have the
same string type (`bytes` or `str`) as the argument(s). Mixing different
string types in one call (for example in `FTPHost.path.join`) isn't
allowed and will cause a `TypeError`. These rules are the same as for
local file system operations.

Although you can pass paths as `str` or `bytes`, the former is
recommended. See below for the reason.

*If* you have directory or file names with non-ASCII characters, you
need to be aware of the encoding the [session factory](#session factory)
(e.g. `ftplib.FTP`) uses. This needs to be the same encoding that the
FTP server software uses for the paths. Note that this may differ from
the encoding of the file system where the remote directories and files
are stored.

The following diagram shows string conversions on the way from your code
to the remote FTP server. The opposite way works analogously, so
encoding steps in the diagram become decoding steps and decoding steps
in the diagram become encoding steps.

Both "branching points" in the upper and lower part of diagrams are
independent, so depending on how you pass paths to ftputil and which
file system API the FTP server uses, there are four possible
combinations overall.

```plaintext
    +-----------+       +-----------+
    | Your code |       | Your code |
    +-----------+       +-----------+
         |                    |
         |  str               |  bytes
         v                    v
    +-------------+     +-------------+  decode with encoding of session,
    | ftputil API |     | ftputil API |  e.g. `ftplib.FTP` instance
    +-------------+     +-------------+
           \               /
            \     str     /
             v           v
           +---------------+  encode with encoding
           |  ftplib API   |  specified in `FTP` instance
           +---------------+
                   |
                   |  bytes
                   v
            +-------------+
            | socket API  |
            +-------------+
               /       \
              /         \                 local / client
    - - - - - / - - - - - \ - - - - - - - - - - - - - - - - - - - - - -
            /             \              remote / server
           /     bytes     \
          v                 v
    +------------+      +------------+  decode with encoding from
    | FTP server |      | FTP server |  FTP server configuration
    +------------+      +------------+
         |                   |
         |  bytes            |  str
         v                   v
    +-------------+      +-------------+
    | remote file |      | remote file |
    | system API  |      | system API  |
    +-------------+      +-------------+
          \                 /
           \      bytes    /
            v             v
         +-------------------+
         |    file system    |
         +-------------------+
```

As you can see at the top of the diagram, if you use `str` objects,
there's one fewer decoding step, and so one fewer source of problems.
If you use `bytes` objects for paths, ftputil tries to get the
encoding for the FTP server from the `encoding` attribute of the
session instance (say, an instance of `ftplib.FTP`). If no `encoding`
attribute is present, a `NoEncodingError` is raised.

All encoding/decoding steps must use the same encoding, the encoding the
server uses (at the bottom of the diagram). If the server uses the bytes
from the socket directly, i.e. without an encoding step, you have to
use the file system encoding.

Until and including Python 3.8, the encoding implicitly assumed by the
`ftplib` module was latin-1, so using `bytes` was the safest strategy.
However, Python 3.9 made the `encoding` configurable via an `ftplib.FTP`
constructor argument `encoding`, *but defaults to UTF-8*.

If you don't pass a [session factory](#session factory) to the
`ftputil.FTPHost` constructor, ftputil will use latin-1 encoding for the
paths. This is the same value as in earlier ftputil versions in
combination with Python 3.8 and earlier.

Summary:

-   If possible, use only ASCII characters in paths.
-   If possible, pass paths to ftputil as `str`, not `bytes`.
-   If you use a custom session factory, the session instances created
    by the factory must have an `encoding` attribute with the name of
    the path encoding to use. If your session instances don't have an
    `encoding` attribute, ftputil raises a `NoEncodingError` when the
    session is created.

### Hidden files and directories

Whether ftputil sees "hidden" files and directories (usually files or
directories whose names start with a dot) depends on the FTP server
configuration. By default, ftputil does *not* use the `-a` option in the
FTP `LIST` command to find hidden files.

To tell the server to list hidden directories and files, set
`FTPHost.use_list_a_option` to `True`:
```python
ftp_host = ftputil.FTPHost(server, user, password, account,
                           session_factory=ftplib.FTP)
ftp_host.use_list_a_option = True
```

Caveats:

-   If the server doesn't understand the `-a` option at all, the server
    may interpret `-a` as the name of a file or directory, which can
    result in odd behavior. Therefore, use `-a` only if you're sure the
    server you're talking to supports it. Another approach is to have
    test code for `-a` support and fall back to not using the option.
-   Even if the server knows about the `-a` option, the server may be
    configured to ignore it.

### `FTPHost` attributes and methods

#### Attributes

-   `curdir`, `pardir`, `sep`

    are strings which denote the current and the parent directory on the
    remote server. `sep` holds the path separator. Though [RFC
    959](https://www.ietf.org/rfc/rfc959.txt) (File Transfer Protocol)
    notes that these values may depend on the FTP server implementation,
    the Unix variants seem to work well in practice, even for non-Unix
    servers.

    Nevertheless, it's recommended that you don't hardcode these values
    for remote paths, but use [FTPHost.path](#FTPHost.path) as you would
    use `os.path` to write platform-independent Python code for local
    filesystems. Keep in mind that most, *but not all*, arguments of
    `FTPHost` methods refer to remote directories or files. For example,
    in [FTPHost.upload](#uploading-and-downloading-files), the first
    argument is a local path and the second argument a remote path.
    Both of these should use their respective path separators.

#### Remote file system navigation

-   `getcwd()`

    returns the absolute current directory on the remote host. This
    method works like `os.getcwd`.

-   `chdir(directory)`

    sets the current directory on the FTP server. This resembles
    `os.chdir`, as you may have expected.

#### Uploading and downloading files

-   `upload(source, target, callback=None)`

    copies a local source file (given by a path, i.e. a string) to the
    remote host under the name target. Both `source` and `target` may
    be absolute paths or relative to their corresponding current
    directory (on the local or the remote host, respectively).

    The file content is always transferred in binary mode.

    The callback, if given, will be invoked for each transferred chunk
    of data:
    ```python
    callback(chunk)
    ```
    where `chunk` is a bytestring. An example usage of a callback method
    is to display a progress indicator.

-   `download(source, target, callback=None)`

    performs a download from the remote source file to a local target
    file. Both `source` and `target` are strings. See the description of
    `upload` for more details.

<a id="upload_if_newer"></a>

-   `upload_if_newer(source, target, callback=None)`

    is similar to the `upload` method. The only difference is that the
    upload is only invoked if the time of the last modification for the
    source file is more recent than that of the target file or the
    target doesn't exist at all. The check for the last modification
    time considers the precision of the timestamps and transfers a file
    "if in doubt". Consequently the code
    ```python
    ftp_host.upload_if_newer("source_file", "target_file")
    time.sleep(10)
    ftp_host.upload_if_newer("source_file", "target_file")
    ```
    might upload the file again if the timestamp of the target file is
    precise up to a minute, which is typically the case because the
    remote datetime is determined by parsing a directory listing from
    the server. To avoid unnecessary transfers, wait at least a minute
    between calls of `upload_if_newer` for the same file. If it still
    seems that a file is uploaded unnecessarily or not when it should
    be, read the subsection on [time shift](#time shift) settings.

    If an upload actually happened, the return value of
    `upload_if_newer` is `True`, else `False`.

    > **Note**
    >
    > The method only checks the existence and/or the
    modification time of the source and target file; it doesn't
    compare any other file properties, say, the file size.

    This also means that if a transfer is interrupted, the remote file
    will have a newer modification time than the local file, and thus
    the transfer won't be repeated if `upload_if_newer` is used a second
    time. There are at least two possibilities after a failed upload:

    -   use `upload` instead of `upload_if_newer`, or
    -   remove the incomplete target file with `FTPHost.remove`, then
        use `upload` or `upload_if_newer` to transfer it again.

<a id="download_if_newer"></a>

-   `download_if_newer(source, target, callback=None)`

    corresponds to `upload_if_newer` but performs a download from the
    server to the local host. Read the descriptions of `download` and
    `upload_if_newer` for more information. If a download actually
    happened, the return value is `True`, else `False`.

#### Time zone correction<span id="time shift"></span>

For `upload_if_newer` and `download_if_newer` to work correctly, the
time zone of the server must be taken into account. By default, ftputil
assumes that the timestamps in server listings are in
[UTC](https://en.wikipedia.org/wiki/Utc).

<a id="set_time_shift"></a>

-   `set_time_shift(time_shift)`

    sets the so-called time shift value, measured in seconds. The time
    shift here is defined as the difference between the time used in
    server listings and UTC.
    ```python
    time_shift = server_time - utc_time
    ```

    For example, a server in Berlin/Germany set to the local time
    (currently UTC+02:00), would require a time shift value of 2 \*
    3600.0 = 7200.0 seconds to be handled correctly by ftputil's
    `upload_if_newer` and `download_if_newer`, as well as the `stat`
    and `lstat` calls.

    Note that servers don't necessarily send their file system listings
    in their local time zone. Some use UTC, which actually makes sense
    because UTC doesn't lead to an ambiguity when there's a switch back
    from the daylight saving time to the "normal" time of the server
    location.

    If the time shift value is invalid, for example its absolute value
    is larger than 24 hours, a `TimeShiftError` is raised.

    > **Note**
    >
    > Versions of ftputil before 4.0.0 used a different definition of
    "time shift", server_time – local_client_time.
    >
    > This had the advantage that the default of 0.0 would be correct *if*
    the server was set to the same time zone as the client where ftputil
    runs. On the other hand, this approach meant that the time shift
    depended on *two* time zones, not only the one used on the server
    side. This could be confusing if server and client *didn't* use the
    same time zone.

    See also [synchronize_times](#synchronize_times) for a way to set
    the time shift with a simple method call. If you can't use
    `synchronize_times` *and* the server uses the same time zone as the
    client, you can set the time shift value with
    ```python
    set_time_shift(
      round( (datetime.datetime.now() - datetime.datetime.utcnow()).seconds, -2 )
    )
    ```

-   `time_shift()`

    returns the currently set time shift value. See `set_time_shift`
    above for the definition of "time shift" in this context.

<a id="synchronize_times"></a>

-   `synchronize_times()`

    synchronizes the local times of the server and the client, so that
    [upload_if_newer](#upload_if_newer) and
    [download_if_newer](#download_if_newer) work as expected, even if
    the client and the server use different time zones. For this to
    work, *all* of the following conditions must be true:

    -   The connection between server and client is established.
    -   The client has write access to the directory that is the
        current directory when `synchronize_times` is called.

    If you can't fulfill these conditions, you can nevertheless set the
    time shift value explicitly with [set_time_shift](#set_time_shift).
    Trying to call `synchronize_times` if the above conditions aren't
    met results in a `TimeShiftError` exception.

#### Creating and removing directories

-   `mkdir(path, [mode])`

    makes the given directory on the remote host. This does *not*
    construct "intermediate" directories that don't already exist. The
    `mode` parameter is ignored; this is for compatibility with
    `os.mkdir` if an `FTPHost` object is passed into a function instead
    of the `os` module. See the explanation in the subsection [Exception
    hierarchy](#exception-hierarchy).

-   `makedirs(path, [mode], exist_ok=False)`

    works similar to `mkdir` (see above), but also makes intermediate
    directories like `os.makedirs`. The `mode` parameter is only there
    for compatibility with `os.makedirs` and is ignored.

    `exist_ok` controls whether the existence of any directory but the
    last in the `path` should be considered an error. If the default
    `False` is used or passed to `makedirs`, ftputil will raise a
    `PermanentError` if any directory but the last already exists.

-   `rmdir(path)`

    removes the given remote directory. If it's not empty, raise a
    `PermanentError`.

-   `rmtree(path, ignore_errors=False, onerror=None)`

    removes the given remote, possibly non-empty, directory tree. The
    interface of this method is rather complex, in favor of
    compatibility with `shutil.rmtree`.

    If `ignore_errors` is set to a true value, errors are ignored. If
    `ignore_errors` is a false value *and* `onerror` isn't set, all
    exceptions occurring during the tree iteration and processing are
    raised. These exceptions are all of type `PermanentError`.

    To distinguish between different kinds of errors, pass in a callable
    for `onerror`. This callable must accept three arguments: `func`,
    `path` and `exc_info`. `func` is a bound method object, *for
    example* `your_host_object.listdir`. `path` is the path that was the
    recent argument of the respective method (`listdir`, `remove`,
    `rmdir`). `exc_info` is the exception info as it is gotten from
    `sys.exc_info`.

    The code of `rmtree` is taken from Python's `shutil` module and
    adapted for `ftputil`.

#### Removing files and links

-   `remove(path)`

    removes a file or link on the remote host, similar to `os.remove`.

-   `unlink(path)`

    is an alias for `remove`.

#### Retrieving information about directories, files and links

-   `listdir(path)`

    returns a list containing the names of the files and directories in
    the given path, similar to
    [os.listdir](https://docs.python.org/library/os.html#os.listdir).
    The special names `.` and `..` are not in the list.

The methods `lstat` and `stat` (and some others) rely on the directory
listing format used by the FTP server. When connecting to a host,
`FTPHost`'s constructor tries to guess the right format, which succeeds
in most cases. However, if you get strange results or `ParserError`
exceptions by a mere `lstat` call, please [enter a
ticket]({{ site.data.urls.tracker }}).

If `lstat` or `stat` give wrong modification dates or times, look at the
methods that deal with time zone differences (see [time zone
correction](#time-zone-correction)).

<a id="FTPHost.lstat"></a>

-   `lstat(path)`

    returns an object similar to that from
    [os.lstat](https://docs.python.org/library/os.html#os.lstat). This
    is a kind of tuple with additional attributes; see the documentation
    of the `os` module for details.

    The result is derived by parsing the output of a `LIST` command on
    the server. Therefore, the result from `FTPHost.lstat` can not
    contain more information than the received text. In particular:

    -   User and group ids can only be determined as strings, not as
        numbers, and that only if the server supplies them. This is
        usually the case with Unix servers but maybe not for other FTP
        servers.

    -   Values for the time of the last modification may be rough,
        depending on the information from the server. For timestamps
        older than a year, this usually means that the precision of the
        modification timestamp value is not better than a day. For newer
        files, the information may be accurate to a minute.

        If the time of the last modification is before the epoch
        (usually 1970-01-01 UTC), set the time of the last modification
        to 0.0.

    -   Links can only be recognized on servers that provide this
        information in the `LIST` output.

    -   Stat attributes that can't be determined at all are set to
        `None`. For example, a line of a directory listing may not
        contain the date/time of a directory's last modification.

    -   There's a special problem with stat'ing the root directory.
        (Stat'ing things *in* the root directory is fine though.) In
        this case, a `RootDirError` is raised. This has to do with the
        algorithm used by `(l)stat`, and I know of no approach which
        mends this problem.

    Currently, `ftputil` recognizes the common Unix-style and
    Microsoft/DOS-style directory formats. If you need to parse output
    from another server type, please write to the [ftputil mailing
    list](https://ftputil.sschwarzer.net/mailinglist). You may consider
    [writing your own parser](#writing-directory-parsers).

<a id="FTPHost.stat"></a>

-   `stat(path)`

    returns `stat` information also for files which are pointed to by a
    link. This method follows multiple links until a regular file or
    directory is found. If an infinite link chain is encountered or the
    target of the last link in the chain doesn't exist, a
    `PermanentError` is raised.

    The limitations of the `lstat` method also apply to `stat`.

<a id="FTPHost.path"></a>

`FTPHost` objects contain an attribute named `path`, similar to
[os.path](https://docs.python.org/library/os.path.html). The following
methods can be applied to the remote host with the same semantics as for
`os.path`:
```python
abspath(path)
basename(path)
commonprefix(path_list)
dirname(path)
exists(path)
getmtime(path)
getsize(path)
isabs(path)
isdir(path)
isfile(path)
islink(path)
join(path1, path2, ...)
normcase(path)
normpath(path)
split(path)
splitdrive(path)
splitext(path)
walk(path, func, arg)
```

Like Python's counterparts under
[os.path](https://docs.python.org/library/os.path.html), `ftputil`'s
`is...` methods return `False` if they can't find the path given by
their argument.

#### Local caching of file system information

Many of the above methods need access to the remote file system to
obtain data on directories and files. To get the most recent data,
*each* call to `lstat`, `stat`, `exists`, `getmtime` etc. would require
fetching a directory listing from the server, which can make the
program *very* slow. This effect is more pronounced for operations
which mostly scan the file system rather than transfer file data.

For this reason, `ftputil` by default saves the results from directory
listings locally and reuses those results. This reduces network accesses
and so speeds up the software a lot. However, since data is more rarely
fetched from the server, the risk of obsolete data also increases. This
will be discussed below.

Caching can be controlled -- if necessary at all -- via the `stat_cache`
object in an `FTPHost`'s namespace. For example, after calling
```python
ftp_host = ftputil.FTPHost(host, user, password)
```
the cache can be accessed as `ftp_host.stat_cache`.

While `ftputil` usually manages the cache quite well, there are two
possible reasons for modifying cache parameters.

The first is when the number of possible entries is too low. You may
notice that when you are processing very large directories and the
program becomes much slower than before. It's common for code to read a
directory with `listdir` and then process the found directories and
files. This can also happen implicitly by a call to `FTPHost.walk`.
The `ftputil` library automatically increases the cache size if
directories with more entries than the current maximum cache size are
to be scanned. Most of the time, this works fine.

However, if you need access to stat data for several directories at the
same time, you may need to increase the cache explicitly. You can do
this with the `resize` method:
```python
ftp_host.stat_cache.resize(20000)
```
where the argument is the maximum number of `lstat` results to store
(the default is 5000). Note that each path on the server, e.g.
"/home/me/some_dir", corresponds to a single cache entry. Methods like
`exists` or `getmtime` all derive their results from a previously
fetched `lstat` result.

The value 5000 above means that the cache will hold *at most* 5000
entries (unless increased automatically by an explicit or implicit
`listdir` call, see above). If more entries are about to be stored,
the entries which haven't been used for the longest time will be
deleted to make place for newer entries.

The second possible reason to change the cache parameters is to avoid
stale cache data. Caching is so effective because it reduces network
accesses. This can also be a disadvantage if the file system data on the
remote server changes after a stat result has been retrieved; the
client, when looking at the cached stat data, will use obsolete
information.

There are two potential ways to get such out-of-date stat data. The
first happens when an `FTPHost` instance modifies a file path for which
it has a cache entry, e.g. by calling `remove` or `rmdir`. Such changes
are handled transparently; the path will be deleted from the cache. A
different matter are changes unknown to the `FTPHost` object which
inspects its cache. Obviously, for example, these are changes by
programs running on the remote host. On the other hand, cache
inconsistencies can also occur if two `FTPHost` objects change a file
system simultaneously:
```python
with (
  ftputil.FTPHost(server, user1, password1) as ftp_host1,
  ftputil.FTPHost(server, user1, password1) as ftp_host2
):
    stat_result1 = ftp_host1.stat("some_file")
    stat_result2 = ftp_host2.stat("some_file")
    ftp_host2.remove("some_file")
    # `ftp_host1` will still see the obsolete cache entry!
    print(ftp_host1.stat("some_file"))
    # Will raise an exception since an `FTPHost` object
    # knows of its own changes.
    print(ftp_host2.stat("some_file"))
```

At first sight, it may appear to be a good idea to have a shared cache
among several `FTPHost` objects. After some thinking, this turns out to
be very error-prone. For example, it won't help with different processes
using `ftputil`. So, if you have to deal with concurrent write/read
accesses to a server, you have to handle them explicitly.

The most useful tool for this is the `invalidate` method. In the example
above, it could be used like this:
```python
with (
  ftputil.FTPHost(server, user1, password1) as ftp_host1,
  ftputil.FTPHost(server, user1, password1) as ftp_host2
):
    stat_result1 = ftp_host1.stat("some_file")
    stat_result2 = ftp_host2.stat("some_file")
    ftp_host2.remove("some_file")
    # Invalidate using an absolute path.
    absolute_path = ftp_host1.path.abspath(
                      ftp_host1.path.join(ftp_host1.getcwd(), "some_file"))
    ftp_host1.stat_cache.invalidate(absolute_path)
    # Will now raise an exception as it should.
    print(ftp_host1.stat("some_file"))
    # Would raise an exception since an `FTPHost` object
    # knows of its own changes, even without `invalidate`.
    print(ftp_host2.stat("some_file"))
```

The method `invalidate` can be used on any *absolute* path, be it a
directory, a file or a link.

By default, the cache entries (if not replaced by newer ones) are stored
for an infinite time. That is, if you start your Python process using
`ftputil` and let it run for three days a stat call may still access
cache data that old. To avoid this, you can set the `max_age` attribute:
```python
    with ftputil.FTPHost(server, user, password) as ftp_host:
        ftp_host.stat_cache.max_age = 60 * 60  # = 3600 seconds
```

This sets the maximum age of entries in the cache to an hour. This means
any entry older won't be retrieved from the cache but its data instead
fetched again from the remote host and then again stored for up to an
hour. To reset <span class="title-ref">max_age</span> to the default of
unlimited age, i.e. cache entries never expire, use `None` as value.

If you are certain that the cache will be in the way, you can disable
and later re-enable it completely with `disable` and `enable`:
```python
with ftputil.FTPHost(server, user, password) as ftp_host:
    ftp_host.stat_cache.disable()
    ...
    ftp_host.stat_cache.enable()
```

During that time, the cache won't be used; all data will be fetched from
the network. After enabling the cache again, its entries will be the
same as when the cache was disabled, that is, entries won't get updated
with newer data during this period. Note that even when the cache is
disabled, the file system data in the code can become inconsistent:
```python
with ftputil.FTPHost(server, user, password) as ftp_host:
    ftp_host.stat_cache.disable()
    if ftp_host.path.exists("some_file"):
        mtime = ftp_host.path.getmtime("some_file")
```
In that case, the file `some_file` may have been removed by another
process between the calls to `exists` and `getmtime`!

#### Iteration over directories

<a id="FTPHost.walk"></a>

-   `walk(top, topdown=True, onerror=None, followlinks=False)`

    iterates over a directory tree, similar to
    [os.walk](https://docs.python.org/2/library/os.html#os.walk).
    Actually, `FTPHost.walk` uses the code from Python with just the
    necessary modifications, so see the linked documentation.

<a id="FTPHost.path.walk"></a>

-   `path.walk(path, func, arg)`

    Similar to `os.path.walk`, the `walk` method in
    [FTPHost.path](#FTPHost.path) can be used, though `FTPHost.walk` is
    probably easier to use.

#### Other methods

-   `close()`

    closes the connection to the remote host. After this, no more
    interaction with the FTP server is possible with this `FTPHost`
    object. Usually you don't need to close an `FTPHost` instance with
    `close` if you set up the instance in a `with` statement.

-   `rename(source, target)`

    renames the source file (or directory) on the FTP server.

<a id="FTPHost.chmod"></a>

-   `chmod(path, mode)`

    sets the access mode (permission flags) for the given path. The mode
    is an integer as returned for the mode by the `stat` and `lstat`
    methods. Be careful: Usually, mode values are written as octal
    numbers, for example 0o755 to make a directory readable and writable
    for the owner, but not writable for the group and others. If you
    want to use such octal values, rely on Python's support for them:
    ```python
    ftp_host.chmod("some_directory", 0o755)
    ```

    Not all FTP servers support the `chmod` command. In case of an
    exception, how do you know if the path doesn't exist or if the
    command itself is invalid? If the FTP server complies with [RFC
    959](https://www.ietf.org/rfc/rfc959.txt), it should return a status
    code 502 if the `SITE CHMOD` command isn't allowed. `ftputil` maps
    this special error response to a `CommandNotImplementedError` which
    is derived from `PermanentError`.

    So you need to code like this:
    ```python
    with ftputil.FTPHost(server, user, password) as ftp_host:
        try:
            ftp_host.chmod("some_file", 0o644)
        except ftputil.error.CommandNotImplementedError:
            # `chmod` not supported
            ...
        except ftputil.error.PermanentError:
            # Possibly a non-existent file
            ...
    ```

    Because the `CommandNotImplementedError` is more specific, you have
    to test for it first.

-   `copyfileobj(source, target, length=64*1024)`

    copies the contents from the file-like object `source` to the
    file-like object `target`. The only difference to
    `shutil.copyfileobj` is the default buffer size. Note that arbitrary
    file-like objects can be used as arguments (e.g. local files,
    remote FTP files or other objects).

    However, the interfaces of `source` and `target` have to match; the
    string type read from `source` must be an accepted string type when
    written to `target`. For example, if you open `source` as a local
    text file and `target` as a remote file object in binary mode, the
    transfer will fail since `source.read` gives unicode strings
    (`str`) whereas `target.write` only accepts byte strings
    (`bytes`).

    See [File-like objects](#file-like-objects) for the construction and
    use of remote file-like objects.

<a id="set_parser"></a>

-   `set_parser(parser)`

    sets a custom parser for FTP directories. Note that you have to pass
    in a parser *instance*, not the class.

    An [extra section](#writing-directory-parsers) shows how to write
    own parsers if the default parsers in `ftputil` don't work for you.

<a id="keep_alive"></a>

-   `keep_alive()`

    attempts to keep the connection to the remote server active in order
    to prevent timeouts from happening. This method is primarily
    intended to keep the underlying FTP connection of an `FTPHost`
    object alive while a file is uploaded or downloaded. This will
    require either an extra thread while the upload or download is in
    progress or calling `keep_alive` from a [callback
    function](#callback function).

    The `keep_alive` method won't help if the connection has already
    timed out. In this case, a `ftputil.error.TemporaryError` is raised.

    If you want to use this method, keep in mind that FTP servers define
    a timeout for a reason. A timeout prevents running out of server
    connections because of clients that never disconnect on their own.

    Note that the `keep_alive` method does *not* affect the "hidden" FTP
    child connections established by `FTPHost.open` (see section
    [FTPHost instances vs. FTP
    connections](#ftphost-instances-vs.-ftp-connections) for details).
    You *can't* use `keep_alive` to avoid a timeout in a stalling
    transfer like this:
    ```python
    with ftputil.FTPHost(server, userid, password) as ftp_host:
        with ftp_host.open("some_remote_file", "rb") as fobj:
            data = fobj.read(100)
            # _Futile_ attempt to avoid file connection timeout.
            for i in range(15):
                time.sleep(60)
                ftp_host.keep_alive()
            # Will raise an `ftputil.error.TemporaryError`.
            data += fobj.read()
    ```

## File-like objects

### Construction

#### Basics

`FTPFile` objects are returned by a call to `FTPHost.open`; never use
the `FTPFile` constructor directly.

The APIs for remote file-like objects are modeled after the APIs of the
built-in `open` function and its return value.

-   `FTPHost.open(path, mode="r", buffering=None, encoding=None, errors=None, newline=None, rest=None)`

    returns a file-like object that refers to the path on the remote
    host. This path may be absolute or relative to the current directory
    on the remote host (this directory can be determined with the
    `getcwd` method). As with local file objects, the default mode is
    "r", i.e. reading text files. Valid modes are "r", "rb", "w", and
    "wb".

    If a file is opened in binary mode, you *must not* specify an
    encoding. On the other hand, if you open a file in text mode, an
    encoding is used. By default, this is the return value of
    `locale.getpreferredencoding`, but you can (and probably should)
    specify an explicit encoding.

    If you open a file in binary mode, the read and write operations use
    `bytes` objects. That is, read operations return `bytes` and write
    operations only accept `bytes`.

    Similarly, text files always work with strings (`str`). Here, read
    operations return string and write operations only accept strings.

    The arguments `buffering`, `errors` and `newline` have the same
    semantics as in
    [open](https://docs.python.org/3/library/functions.html#open).

    If the file is opened in binary mode, you may pass 0 or a positive
    integer for the `rest` argument. The argument is passed to the
    underlying FTP session instance (for example an instance of
    `ftplib.FTP`) to start reading or writing at the given byte offset.
    For example, if a remote file contains the letters "abcdef" in ASCII
    encoding, `rest=3` will start reading at "d".


    > **Warning**
    >
    > If you pass `rest` values which point *after* the file, the behavior
    is undefined and may even differ from one FTP server to another.
    Therefore, use the `rest` argument only for error recovery in case
    of interrupted transfers. You need to keep track of the transferred
    data so that you can provide a valid `rest` argument for a resumed
    transfer.

`FTPHost.open` can also be used in a `with` statement:
```python
import ftputil

with ftputil.FTPHost(...) as ftp_host:
    ...
    with ftp_host.open("new_file", "w", encoding="utf8") as fobj:
        fobj.write("This is some text.")
```

At the end of the `with` block, the remote file will be closed
automatically.

If something goes wrong during the construction of the file or in the
body of the `with` statement, the file will be closed as well.
Exceptions from the `with` body will be propagated.

### Attributes and methods

The methods
```python
close()
read([count])
readline([count])
readlines()
write(data)
writelines(string_sequence)
```
and the attribute `closed` have the same semantics as for file objects
of a local file system. The iterator protocol is supported as well,
i.e. you can use a loop to read a file line by line:
```python
with ftputil.FTPHost(server, user, password) as ftp_host:
    with ftp_host.open("some_file") as input_file:
        for line in input_file:
            # Do something with the line, e.g.
            print(line.strip().replace("ftplib", "ftputil"))
```

For more on file objects, see the section [File
objects](https://docs.python.org/3/glossary.html#term-file-object) in
the Python Library Reference.

## `FTPHost` instances vs. FTP connections

This section explains why keeping an `FTPHost` instance "alive" without
timing out sometimes isn't trivial. If you always finish your FTP
operations in time, you don't need to read this section.

The file transfer protocol is a stateful protocol. That means an FTP
connection always is in a certain state. Each of these states can only
change to certain other states under certain conditions triggered by the
client or the server.

One of the consequences is that a single FTP connection can't be used at
the same time, say, to transfer data on the FTP data channel and to
create a directory on the remote host.

For example, consider this:
```python
>>> import ftplib
>>> ftp = ftplib.FTP(server, user, password)
>>> ftp.pwd()
'/'
>>> # Start transfer. `CONTENTS` is a text file on the server.
>>> socket = ftp.transfercmd("RETR CONTENTS")
>>> socket
<socket._socketobject object at 0x7f801a6386e0>
>>> ftp.pwd()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/lib64/python2.7/ftplib.py", line 578, in pwd
    return parse257(resp)
  File "/usr/lib64/python2.7/ftplib.py", line 842, in parse257
    raise error_reply, resp
ftplib.error_reply: 226-File successfully transferred
226 0.000 seconds (measured here), 5.60 Mbytes per second
>>>
```

Note that `ftp` is a single FTP connection, represented by an
`ftplib.FTP` instance, not an `ftputil.FTPHost` instance.

On the other hand, consider this:
```python
>>> import ftputil
>>> ftp_host = ftputil.FTPHost(server, user, password)
>>> ftp_host.getcwd()
>>> fobj = ftp_host.open("CONTENTS")
>>> fobj
<ftputil.file.FTPFile object at 0x7f8019d3aa50>
>>> ftp_host.getcwd()
u'/'
>>> fobj.readline()
u'Contents of FTP test directory\n'
>>> fobj.close()
>>>
```

To be able to start a file transfer (i.e. open a remote file for
reading or writing) and still be able to use other FTP commands, ftputil
uses a trick. For every remote file, ftputil creates a new FTP
connection, called a child connection in the ftputil source code.
(Actually, FTP connections belonging to closed remote files are re-used
if they haven't timed out yet.)

In most cases this approach isn't noticeable by code using ftputil.
However, the nice abstraction of dealing with a single FTP connection
falls apart if one of the child connections times out. For example, if
you open a remote file and work only with the initial "main" connection
to navigate the file system, the FTP connection for the remote file may
eventually time out.

While it's often relatively easy to prevent the "main" connection from
timing out it's unfortunately practically impossible to do this for a
remote file connection (apart from transferring some data, of course).
For this reason, [FTPHost.keep_alive](#keep_alive) affects only the main
connection. Child connections may still time out if they're idle for too
long.

Some more details:

-   A kind of "straightforward" way of keeping the main connection alive
    would be to call `ftp_host.getcwd()`. However, this doesn't work
    because ftputil caches the current directory and returns it without
    actually contacting the server. That's the main reason why there's a
    `keep_alive` method since it calls `pwd` on the FTP connection
    (i.e. the session object), which isn't a public attribute.
-   Some servers define not only an idle timeout but also a transfer
    timeout. This means the connection times out unless there's some
    transfer on the data channel for this connection. So ftputil's
    `keep_alive` doesn't prevent this timeout, but an
    `ftp_host.listdir(ftp_host.curdir)` call should do it. However, this
    transfers the data for the whole directory listing which might take
    some time if the directory has many entries.

Bottom line: If you can, you should organize your FTP actions so that
you finish everything before a timeout happens. If that isn't
possible, you need to write code that can reopen FTP connections and
resume operations on them.

## Writing directory parsers

`ftputil` recognizes the two most widely-used FTP directory formats,
Unix and MS style, and adjusts itself automatically. Almost every FTP
server uses one of these formats.

However, if your server uses a format which is different from the two
provided by `ftputil`, you can plug in a custom parser with a single
method call and have `ftputil` use this parser.

For this, you need to write a parser class by inheriting from the class
`Parser` in the `ftputil.stat` module. Here's an example:
```python
import ftputil.error
import ftputil.stat

class XyzParser(ftputil.stat.Parser):
    """
    Parse the default format of the FTP server of the XYZ
    corporation.
    """

    def parse_line(self, line, time_shift=0.0):
        """
        Parse a `line` from the directory listing and return a
        corresponding `StatResult` object. If the line can't
        be parsed, raise `ftputil.error.ParserError`.

        The `time_shift` argument can be used to fine-tune the
        parsing of dates and times. See the class
        `ftputil.stat.UnixParser` for an example.
        """
        # Split the `line` argument and examine it further; if
        # something goes wrong, raise an `ftputil.error.ParserError`.
        ...
        # Make a `StatResult` object from the parts above.
        stat_result = ftputil.stat.StatResult(...)
        # `_st_name`, `_st_target` and `_st_mtime_precision` are optional.
        stat_result._st_name = ...
        stat_result._st_target = ...
        stat_result._st_mtime_precision = ...
        return stat_result

    # Define `ignores_line` only if the default in the base class
    # doesn't do enough!
    def ignores_line(self, line):
        """
        Return a true value if the line should be ignored. For
        example, the implementation in the base class handles
        lines like "total 17". On the other hand, if the line
        should be used for stat'ing, return a false value.
        """
        is_total_line = super().ignores_line(line)
        my_test = ...
        return is_total_line or my_test
```

A `StatResult` object is similar to the value returned by
[os.stat](https://docs.python.org/library/os.html#os.stat) and is
usually built with statements like
```python
stat_result = StatResult(
                (st_mode, st_ino, st_dev, st_nlink, st_uid,
                 st_gid, st_size, st_atime, st_mtime, st_ctime))
stat_result._st_name = ...
stat_result._st_target = ...
stat_result._st_mtime_precision = ...
```
with the arguments of the `StatResult` constructor described in the
following table.

| Index | Attribute | `os.stat` type | `StatResult` type | Notes |
|-------|-----------|----------------|-------------------|-------|
| 0     | st\_mode  | int            | int               |       |
| 1     | st\_ino   | int            | int               |       |
| 2     | st\_dev   | int            | int               |       |
| 3     | st\_nlink | int            | int               |       |
| 4     | st\_uid   | int            | str               | usually only available as string |
| 5     | st\_gid   | int            | str               | usually only available as string |
| 6     | st\_size  | int            | int               |       |
| 7     | st\_atime | int/float      | float             |       |
| 8     | st\_mtime | int/float      | float             |       |
| 9     | st\_ctime | int/float      | float             |       |
| -     | \_st\_name | -             | str               | file name without directory part |
| -     | \_st\_target | -           | str               | link target (may be absolute or relative) |
| -     | \_st\_mtime_precision | -  | int               | st_mtime precision in seconds |

If you can't extract all the desirable data from a line (for example,
the MS format doesn't contain any information about the owner of a
file), set the corresponding values in the `StatResult` instance to
`None`.

Parser classes can use several helper methods which are defined in the
class `Parser`:

-   `parse_unix_mode` parses strings like "drwxr-xr-x" and returns an
    appropriate `st_mode` integer value.
-   `parse_unix_time` returns a float number usable for the `st_...time`
    values by parsing arguments like "Nov"/"23"/"02:33" or
    "May"/"26"/"2005". Note that the method expects the timestamp string
    already split at whitespace.
-   `parse_ms_time` parses arguments like "10-23-01"/"03:25PM" and
    returns a float number like from `time.mktime`. Note that the method
    expects the timestamp string already split at whitespace.

Additionally, there's an attribute `_month_numbers` which maps lowercase
three-letter month abbreviations to integers.

For more details, see the two "standard" parsers `UnixParser` and
`MSParser` in the module `ftputil/stat.py`.

To actually *use* the parser, call the method [set_parser](#set_parser)
of the `FTPHost` instance.

If you can't write a parser or don't want to, please ask on the [ftputil
mailing list](https://ftputil.sschwarzer.net/mailinglist). Possibly
someone has already written a parser for your server or can help with
it.

## Bugs and limitations

-   `ftputil` needs at least Python 3.6 to work.
-   Whether `ftputil` "sees" "hidden" directory and file names (i.e.
    names starting with a dot) depends on the configuration of the FTP
    server. See [Hidden files and
    directories](#hidden-files-and-directories) for details.
-   Due to the implementation of `lstat` it can't return a sensible
    value for the root directory `/` though stat'ing entries *in* the
    root directory isn't a problem. If you know an implementation that
    can do this, please let me know. The root directory is handled
    appropriately in `FTPHost.path.exists/isfile/isdir/islink`, though.
-   In multithreaded programs, you can have each thread use one or more
    `FTPHost` instances as long as no instance is shared with other
    threads.
-   Currently, it is not possible to continue an interrupted upload or
    download. Contact me if this causes problems for you.
-   There's exactly one cache for `lstat` results for each `FTPHost`
    object, i.e. there's no sharing of cache results determined by
    several `FTPHost` objects. See [Local caching of file system
    information](#local-caching-of-file-system-information) for the
    reasons.

## Files

If not overwritten via installation options, the `ftputil` files reside
in the `ftputil` package.

The files `test_*.py` and `scripted_session.py` are for unit-testing. If
you only *use* `ftputil`, i.e. *don't* modify it, you can delete these
files.

## References

-   Postel J, Reynolds J. 1985. [RFC 959 - File Transfer Protocol
    (FTP)](https://www.ietf.org/rfc/rfc959.txt).
-   Python Software Foundation. 2020. [The Python Standard
    Library](https://docs.python.org/library/index.html).

## Authors

`ftputil` is written by Stefan Schwarzer \<<sschwarzer@sschwarzer.net>\>
and contributors (see `doc/contributors.txt`).

The original `lrucache` module was written by Evan Prodromou
\<<evan@prodromou.name>\>.

Feedback is appreciated. :-)
