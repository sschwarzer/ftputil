# Copyright (C) 2014-2021, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Unit tests for session factory helpers.
"""

import ftplib
import sys

import ftputil.path_encoding
import ftputil.session
import ftputil.tool


# Inherit from `ftplib.FTP` to get past the subclass check in
# `ftputil.session.session_factory`.
class MockSession(ftplib.FTP):
    """
    Mock session base class to determine if all expected calls have happened.
    """

    encoding = ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING

    def __init__(self, encoding=None):
        self.calls = []
        if encoding is not None:
            self.encoding = encoding

    def add_call(self, *args):
        self.calls.append(args)

    def connect(self, host, port):
        self.add_call("connect", host, port)

    def set_debuglevel(self, value):
        self.add_call("set_debuglevel", value)

    def login(self, user, password):
        self.add_call("login", user, password)

    def set_pasv(self, flag):
        self.add_call("set_pasv", flag)


class EncryptedMockSession(MockSession):
    def auth_tls(self):
        self.add_call("auth_tls")

    def prot_p(self):
        self.add_call("prot_p")


class TestSessionFactory:
    """
    Test if session factories created by `ftputil.session.session_factory`
    trigger the expected calls.
    """

    def test_defaults(self):
        """
        Test defaults (apart from base class).
        """
        factory = ftputil.session.session_factory(base_class=MockSession)
        session = factory("host", "user", "password")
        assert session.calls == [("connect", "host", 21), ("login", "user", "password")]

    def test_different_port(self):
        """
        Test setting the command channel port with `port`.
        """
        factory = ftputil.session.session_factory(base_class=MockSession, port=2121)
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 2121),
            ("login", "user", "password"),
        ]

    def test_use_passive_mode(self):
        """
        Test explicitly setting passive/active mode with `use_passive_mode`.
        """
        # Passive mode
        factory = ftputil.session.session_factory(
            base_class=MockSession, use_passive_mode=True
        )
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("login", "user", "password"),
            ("set_pasv", True),
        ]
        # Active mode
        factory = ftputil.session.session_factory(
            base_class=MockSession, use_passive_mode=False
        )
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("login", "user", "password"),
            ("set_pasv", False),
        ]

    def test_encrypt_data_channel(self):
        """
        Test request to call `prot_p` with `encrypt_data_channel`.
        """
        # With encrypted data channel (default for encrypted session).
        factory = ftputil.session.session_factory(base_class=EncryptedMockSession)
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("login", "user", "password"),
            ("prot_p",),
        ]
        #
        factory = ftputil.session.session_factory(
            base_class=EncryptedMockSession, encrypt_data_channel=True
        )
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("login", "user", "password"),
            ("prot_p",),
        ]
        # Without encrypted data channel.
        factory = ftputil.session.session_factory(
            base_class=EncryptedMockSession, encrypt_data_channel=False
        )
        session = factory("host", "user", "password")
        assert session.calls == [("connect", "host", 21), ("login", "user", "password")]

    def test_encoding(self):
        """
        Test setting the default encoding and a custom encoding.
        """
        # Default encoding
        factory = ftputil.session.session_factory(
            base_class=MockSession,
        )
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("login", "user", "password"),
        ]
        assert session.encoding == ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING
        # Custom encoding
        factory = ftputil.session.session_factory(
            base_class=MockSession,
            encoding="UTF-8",
        )
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("login", "user", "password"),
        ]
        assert session.encoding == "UTF-8"

    def test_debug_level(self):
        """
        Test setting the debug level on the session.
        """
        factory = ftputil.session.session_factory(base_class=MockSession, debug_level=1)
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("set_debuglevel", 1),
            ("login", "user", "password"),
        ]
