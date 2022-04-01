---
permalink: /faq
title: "FAQ"
---

## Where can I get the latest version?

See the [installation](/installation) page.

Announcements for new versions will be sent to the [mailing
list](/community#mailing-list).

## Is there a mailing list on `ftputil`?

Yes, please see the [community](/community#mailing-list) page.

## I think I found a bug. What should I do?

Make sure that you already read the [documentation](/documentation)
(the "bug" might be intended behavior)
and tried the [latest version](/installation) of `ftputil` (where the
bug might have already been fixed).

If neither of these helps, please reach out on the [mailing
list](/community).

By the way, also send a mail if you think something in the
documentation isn't easy to understand. Improving on such problems in
the documentation should make it easier for other users.

## Does `ftputil` support TLS?

There are two ways to get TLS support with ftputil:

-   The `ftplib` library has a class `FTP_TLS`, which you can use for the
    `session_factory` keyword argument in the `FTPHost` constructor. You
    can't use the class directly though *if* you need additional setup
    code in comparison to `ftplib.FTP`, for example calling `prot_p`, to
    secure the data connection. On the other hand,
    [ftputil.session.session_factory](#session-factories) can be used to
    create a custom session factory.

-   If you have other requirements that `session_factory` can't fulfill,
    you may create your own session factory by inheriting from
    `ftplib.FTP_TLS`:
    ```python
    import ftplib

    import ftputil


    class FTPTLSSession(ftplib.FTP_TLS):

        def __init__(self, host, user, password):
            ftplib.FTP_TLS.__init__(self)
            self.connect(host, port)
            self.login(user, password)
            # Set up encrypted data connection.
            self.prot_p()
            ...

    # Note the `session_factory` parameter. Pass the class, not
    # an instance.
    with ftputil.FTPHost(server, user, password,
                         session_factory=FTPTLSSession) as ftp_host:
        # Use `ftp_host` as usual.
        ...
    ```

## How do I connect to a non-default port?

By default, an instantiated `FTPHost` object connects on the usual FTP
port. If you have to use a different port, refer to the section [Session
factories](/documentation#session-factories).

## How do I set active or passive mode?

Please see the section [Session
factories](/documentation#session-factories).

## How can I debug an FTP connection problem?

You can do this with a session factory. See [Session
factories](/documentation#session-factories).

If you want to change the debug level only temporarily after the
connection is established, you can reach the [session
object](/documentation#session-factories) as the `_session` attribute
of the `FTPHost` instance and call `_session.set_debuglevel`. Note
that the `_session` attribute should *only* be accessed for debugging.
Calling arbitrary `ftplib.FTP` methods on the session object may
*cause* bugs!

## What to do about unnecessary uploads/downloads to/from a server?

The methods `FTPHost.upload_if_newer` and `FTPHost.download_if_newer`
should only transfer a file if the source is newer than the target.

If that doesn't seem to work, it's most likely for one of these
reasons:
- The client (the program using ftputil) doesn't know the time zone
  difference to the server. Please see the section on [time zone
  correction](/documentation/#time-zone-correction). It may even be
  sufficient to call
  [synchronize_times](/documentation/#synchronize_times).
- Timestamps on the server usually are only precise up to minutes.
  Since ftputil, if "in doubt", errs on the side of transferring too
  much data rather than too little, ftputil transfers a file if the
  source *may* be newer than the target.

## When I use `ftputil`, all I get is a `ParserError` exception. Why?

The FTP server you connect to may use a directory format that
`ftputil` doesn't understand. You can either write and [plug in your
own parser](/documentation/#writing-directory-parsers) or ask on the
[mailing list](/community#mailing-list) for help.

## `isdir`, `isfile` or `islink` incorrectly return `False`. Why?

Like Python's counterparts under
[os.path](https://docs.python.org/library/os.path.html), `ftputil`'s
methods return `False` if they can't find the given path.

Probably you used `listdir` on a directory and called `is...()` on the
returned names. But if the argument for `listdir` wasn't the current
directory, the paths won't be found and so all `is...()` variants will
return `False`.

## What should I do if I don't find an answer to my problem in this document?

Please send an email with your problem report or question to the
[ftputil mailing list](/community#mailing-list), and we'll see what we
can do for you. :-)
