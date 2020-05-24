# Copyright (C) 2014-2018, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Session factory factory (the two "factory" are intentional :-) ) for ftputil.
"""

import ftplib


__all__ = ["session_factory"]


# In a way, it would be appropriate to call this function
# `session_factory_factory`, but that's cumbersome to use. Think of the
# function returning a session factory and the shorter name should be fine.
def session_factory(
    base_class=ftplib.FTP,
    port=21,
    use_passive_mode=None,
    *,
    encrypt_data_channel=True,
    debug_level=None,
):
    """
    Create and return a session factory according to the keyword arguments.

    base_class: Base class to use for the session class (e. g. `ftplib.FTP_TLS`
    or `M2Crypto.ftpslib.FTP_TLS`, default is `ftplib.FTP`).

    port: Port number (integer) for the command channel (default 21). If you
    don't know what "command channel" means, use the default or use what the
    provider gave you as "the FTP port".

    use_passive_mode: If `True`, explicitly use passive mode. If `False`,
    explicitly don't use passive mode. If `None` (default), let the
    `base_class` decide whether it wants to use active or passive mode.

    encrypt_data_channel: If `True` (the default), call the `prot_p` method of
    the base class if it has the method. If `False` or `None` (`None` is the
    default), don't call the method.

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

    class Session(base_class):
        """
        Session factory class created by `session_factory`.
        """

        def __init__(self, host, user, password):
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

    return Session
