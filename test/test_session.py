# Copyright (C) 2014-2023, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Unit tests for session factory helpers.
"""

import ftplib
import sys

import pytest

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

    def login(self, user, password):
        self.add_call("login", user, password)

    def sendcmd(self, command):
        self.add_call("sendcmd", command)

    def set_debuglevel(self, value):
        self.add_call("set_debuglevel", value)

    def set_pasv(self, flag):
        self.add_call("set_pasv", flag)


class MockSessionWithSendcmdFTPError(MockSession):
    """
    Mock session where `sendcmd("OPTS UTF8 ON")` raises a `PermanentError`.
    """

    FTPError = ftputil.error.PermanentError

    def sendcmd(self, command):
        raise self.FTPError("sendcmd raised exception")


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

    @pytest.mark.parametrize(
        "encoding, send_opts_utf8_on, expected_encoding, expected_session_calls_after_login",
        [
            (None, None, ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING, []),
            (None, False, ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING, []),
            ("UTF-8", None, "UTF-8", [("sendcmd", "OPTS UTF8 ON")]),
            ("UTF-8", False, "UTF-8", []),
            ("UTF-8", True, "UTF-8", [("sendcmd", "OPTS UTF8 ON")]),
            ("latin1", None, "latin1", []),
            ("latin1", False, "latin1", []),
        ],
    )
    def test_encoding_and_send_opts_utf8_on(
        self,
        encoding,
        send_opts_utf8_on,
        expected_encoding,
        expected_session_calls_after_login,
    ):
        """
        If `encoding` and `send_opts_utf8_on` have the given values, the result
        should be the same as documented.

        This collection of tests doesn't cover the combinations of `encoding`
        and `send_opts_utf8_on` that result in exceptions.
        """
        factory = ftputil.session.session_factory(
            base_class=MockSession,
            encoding=encoding,
            send_opts_utf8_on=send_opts_utf8_on,
        )
        session = factory("host", "user", "password")
        expected_session_calls = [
            ("connect", "host", 21),
            ("login", "user", "password"),
        ] + expected_session_calls_after_login
        assert session.encoding == expected_encoding

    @pytest.mark.parametrize("send_opts_utf8_on", [None, True])
    def test_ftp_errors_for_send_opts_utf8_on(self, send_opts_utf8_on):
        """
        - If `encoding` is "UTF-8" and `send_opts_utf8_on` is `None`, FTP
          errors should be caught and ignored.

        - If `encoding` is "UTF-8" and `send_opts_utf8_on` is `True`, FTP
          errors should _not_ be caught.
        """
        factory = ftputil.session.session_factory(
            base_class=MockSessionWithSendcmdFTPError,
            encoding="UTF-8",
            send_opts_utf8_on=send_opts_utf8_on,
        )
        if send_opts_utf8_on is None:
            session = factory("host", "user", "password")
            expected_session_calls = [
                ("connect", "host", 21),
                ("login", "user", "password"),
                ("sendcmd", "OPTS UTF8 ON"),
            ]
            assert session.encoding == "UTF-8"
        elif send_opts_utf8_on is True:
            with pytest.raises(MockSessionWithSendcmdFTPError.FTPError):
                session = factory("host", "user", "password")

    @pytest.mark.parametrize(
        "encoding, send_opts_utf8_on",
        [
            (None, True),
            ("latin1", True),
        ],
    )
    def test_invalid_encoding_and_send_opts_utf8_on(
        self,
        encoding,
        send_opts_utf8_on,
    ):
        """
        If the combination of `encoding` and `send_opts_utf8_on` is invalid, a
        `ValueError` should be raised.
        """
        factory = ftputil.session.session_factory(
            base_class=MockSession,
            encoding=encoding,
            send_opts_utf8_on=send_opts_utf8_on,
        )
        with pytest.raises(ValueError):
            _session = factory("host", "user", "password")

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
