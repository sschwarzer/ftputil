# encoding: utf-8
# Copyright (C) 2014, Stefan Schwarzer

"""
Session factory class for use with M2Crypto.

Different from Python's `ftplib.FTP_TLS`, `M2Crypto.ftpslib.FTP_TLS`
uses a special socket object. This object's `sendall` method doesn't
work as expected for unicode arguments.

This module provides a workaround by wrapping the socket object so
that the argument to `sendall` is converted to a byte string before
being used.

See ticket #78 for details.
"""

from __future__ import unicode_literals

import M2Crypto

import ftputil.tool


class M2CryptoSession(M2Crypto.ftpslib.FTP_TLS):

    # Argument names as in `ftplib.FTP_TLS`.
    def __init__(self, host, user, passwd):
        # Can't use `super` because `M2Crypto.ftpslib.FTP_TLS` is a
        # classic class.
        M2Crypto.ftpslib.FTP_TLS.__init__(self)
        self.connect(host, 21)
        self.auth_tls()
        self.login(user, passwd)
        self.prot_p()
        self._fix_socket()

    def _fix_socket(self):
        """
        Change the socket object so that arguments to `sendall`
        are converted to byte strings before being used.
        """
        original_sendall = self.sock.sendall
        # Bound method, therefore no `self` argument.
        def sendall(data):
            data = ftputil.tool.as_bytes(data)
            return original_sendall(data)
        self.sock.sendall = sendall
