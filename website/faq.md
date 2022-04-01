---
permalink: /faq
title: "FAQ"
---

## Where can I get the latest version?

See the [download page](https://ftputil.sschwarzer.net/download).
Announcements will be sent to the [mailing
list](https://ftputil.sschwarzer.net/mailinglist).

## Is there a mailing list on `ftputil`?

Yes, please visit <https://ftputil.sschwarzer.net/mailinglist> to
subscribe or read the archives.

## I found a bug! What now?

Before reporting a bug, make sure that you already read this manual and
tried the [latest version](https://ftputil.sschwarzer.net/download) of
`ftputil`. There the bug might have already been fixed.

Please see <{{ site.data.urls.tracker }}> for
guidelines on entering a bug in `ftputil`'s ticket system. If you are
unsure if the behaviour you found is a bug or not, you should write to
the [ftputil mailing list]({{ site.data.urls.mailing_list }}).
*Never* include confidential information (user id, password, file names,
etc.) in the problem report! Be careful!

## Does `ftputil` support TLS?

`ftputil` has no *built-in* TLS support.

However, there are two ways to get TLS support with ftputil:

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
factories](#session-factories).

## How do I set active or passive mode?

Please see the section [Session factories](#session-factories).

## How can I debug an FTP connection problem?

You can do this with a session factory. See [Session
factories](#session-factories).

If you want to change the debug level only temporarily after the
connection is established, you can reach the [session
object](#session-factories) as the `_session` attribute of the `FTPHost`
instance and call `_session.set_debuglevel`. Note that the `_session`
attribute should *only* be accessed for debugging. Calling arbitrary
`ftplib.FTP` methods on the session object may *cause* bugs!

## Conditional upload/download to/from a server in a different time zone

You may find that `ftputil` uploads or downloads files unnecessarily, or
not when it should. Please see the section on [time zone
correction](#time-zone-correction). It may even be sufficient to call
[synchronize_times](#synchronize_times).

## When I use `ftputil`, all I get is a `ParserError` exception

The FTP server you connect to may use a directory format that `ftputil`
doesn't understand. You can either write and [plug in your own
parser](#writing-directory-parsers) or ask on the [mailing
list](https://ftputil.sschwarzer.net/mailinglist) for help.

## `isdir`, `isfile` or `islink` incorrectly return `False`

Like Python's counterparts under
[os.path](https://docs.python.org/library/os.path.html), `ftputil`'s
methods return `False` if they can't find the given path.

Probably you used `listdir` on a directory and called `is...()` on the
returned names. But if the argument for `listdir` wasn't the current
directory, the paths won't be found and so all `is...()` variants will
return `False`.

## I don't find an answer to my problem in this document

Please send an email with your problem report or question to the
[ftputil mailing list](https://ftputil.sschwarzer.net/mailinglist), and
we'll see what we can do for you. :-)
