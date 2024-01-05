# Copyright (C) 2014-2024, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Session factory factory (the two "factory" are intentional :-) ) for ftputil.
"""

import ftplib

import ftputil.error
import ftputil.tool


__all__ = ["session_factory"]


def _maybe_send_opts_utf8_on(session, encoding):
    """
    If the requested encoding is UTF-8 and the server supports the `UTF8`
    feature, send "OPTS UTF8 ON".

    See https://datatracker.ietf.org/doc/html/rfc2640.html .
    """
    if ((encoding is None) and ftputil.path_encoding.RUNNING_UNDER_PY39_AND_UP) or (
        encoding in ["UTF-8", "UTF8", "utf-8", "utf8"]
    ):
        feat_output = session.sendcmd("FEAT")
        server_supports_opts_utf8_on = False
        for line in feat_output.splitlines():
            # The leading space is important. See RFC 2640.
            if line.upper().rstrip() == " UTF8":
                server_supports_opts_utf8_on = True
        if server_supports_opts_utf8_on:
            session.sendcmd("OPTS UTF8 ON")


# In a way, it would be appropriate to call this function
# `session_factory_factory`, but that's cumbersome to use. Think of the
# function returning a session factory and the shorter name should be fine.
def session_factory(
    base_class=ftplib.FTP,
    port=21,
    use_passive_mode=None,
    *,
    encrypt_data_channel=True,
    encoding=None,
    debug_level=None,
):
    """
    Create and return a session factory according to the keyword arguments.

    base_class: Base class to use for the session class (e. g. `ftplib.FTP_TLS`
    or `M2Crypto.ftpslib.FTP_TLS`, the default is `ftplib.FTP`).

    port: Port number (integer) for the command channel (default 21). If you
    don't know what "command channel" means, use the default or use what the
    provider gave you as "the FTP port".

    use_passive_mode: If `True`, explicitly use passive mode. If `False`,
    explicitly don't use passive mode. If `None` (default), let the
    `base_class` decide whether it wants to use active or passive mode.

    encrypt_data_channel: If `True` (the default), call the `prot_p` method of
    the base class if it has the method. If `False` or `None` (`None` is the
    default), don't call the method.

    encoding: Encoding (str) to use for directory and file paths, or `None`.
    Unicode (`str`) paths will be encoded with this encoding. Bytes paths are
    assumed to be in this encoding. The default (equivalent to passing `None`)
    is to use the default encoding of the `base_class` argument. Note that this
    encoding has changed from Python 3.8 to 3.9.

    In Python 3.8 and lower, the default path encoding is "latin-1"; in Python
    3.9, the default path encoding is "utf-8". Therefore, if you want an
    encoding that's independent of the Python version, pass an explicit
    `encoding`.

    Using a non-`None` `encoding` is only supported if `base_class` is
    `ftplib.FTP` or a subclass of it.

    debug_level: Debug level (integer) to be set on a session instance. The
    default is `None`, meaning no debugging output.

    This function should work for the base classes `ftplib.FTP`,
    `ftplib.FTP_TLS`. Other base classes should work if they use the same API
    as `ftplib.FTP`.

    Usage example:

      my_session_factory = session_factory(
                             base_class=ftplib.FTP_TLS,
                             use_passive_mode=True,
                             encrypt_data_channel=True)
      with ftputil.FTPHost(host, user, password,
                           session_factory=my_session_factory) as host:
        ...
    """
    if not isinstance(base_class, type):
        raise ValueError(f"`base_class` must be a class, but is {base_class!r}")
    if (encoding is not None) and (not issubclass(base_class, ftplib.FTP)):
        raise ValueError(
            f"`encoding` is only supported for `ftplib.FTP` and subclasses, "
            f"but base class is {base_class!r}"
        )

    class Session(base_class):
        """
        Session factory class created by `session_factory`.
        """

        # In Python 3.8 and below, the `encoding` class attribute was never
        # documented, but setting it is the only way to set a custom encoding
        # for remote file system paths. Since we set the encoding on the class
        # level, all instances created from this class will share this
        # encoding. That's ok because the user asked for a specific encoding of
        # the _factory_ when calling `session_factory`.
        #
        # Python 3.9 is the first Python version to have a documented way to
        # set a custom encoding (per instance).
        #
        # XXX: The following heuristic doesn't cover the case that we run under
        # Python 3.8 or earlier _and_ have a base class with an `encoding`
        # argument. Also, the heuristic will fail if we run under Python 3.9,
        # but have a base class that overrides the constructor so that it
        # doesn't support the `encoding` argument anymore.
        def __init__(self, host, user, password):
            if (
                encoding is not None
            ) and ftputil.path_encoding.RUNNING_UNDER_PY39_AND_UP:
                super().__init__(encoding=encoding)
            else:
                super().__init__()
            self.connect(host, port)
            if debug_level is not None:
                self.set_debuglevel(debug_level)
            self.login(user, password)
            # `set_pasv` can be called with `True` (causing passive mode) or
            # `False` (causing active mode).
            if use_passive_mode is not None:
                self.set_pasv(use_passive_mode)
            if encrypt_data_channel and hasattr(base_class, "prot_p"):
                self.prot_p()
            _maybe_send_opts_utf8_on(self, encoding)

    if (encoding is not None) and not ftputil.path_encoding.RUNNING_UNDER_PY39_AND_UP:
        Session.encoding = encoding
    return Session
