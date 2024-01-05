# Copyright (C) 2014-2024, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Unit tests for session factory helpers.
"""

import ftplib
import functools
import sys

import pytest

import ftputil.path_encoding
import ftputil.session
import ftputil.tool


UTF8_FEAT_STRING = " UTF8\r\n"


# Inherit from `ftplib.FTP` to get past the subclass check in
# `ftputil.session.session_factory`.
class MockSession(ftplib.FTP):
    """
    Mock session base class to determine if all expected calls have happened.
    """

    encoding = ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING

    def __init__(self, encoding=None, feat_command_output=""):
        self.calls = []
        if encoding is not None:
            self.encoding = encoding
        self._feat_command_output = feat_command_output

    def add_call(self, *args):
        self.calls.append(args)

    def connect(self, host, port):
        self.add_call("connect", host, port)

    def login(self, user, password):
        self.add_call("login", user, password)

    def sendcmd(self, command):
        self.add_call("sendcmd", command)
        if command == "FEAT":
            return self._feat_command_output
        else:
            # Dummy
            return ""

    def set_debuglevel(self, value):
        self.add_call("set_debuglevel", value)

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

    @staticmethod
    def _expected_session_calls_for_encoding_handling(encoding, feat_command_output):
        """
        Return the FTP session calls that the session factory should perform.
        """
        if encoding is None:
            encoding = ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING
        if encoding.upper() == "UTF-8":
            if feat_command_output == UTF8_FEAT_STRING:
                return [("sendcmd", "FEAT"), ("sendcmd", "OPTS UTF8 ON")]
            else:
                return [("sendcmd", "FEAT")]
        else:
            return []

    def test_defaults(self):
        """
        Test defaults (apart from base class).
        """
        factory = ftputil.session.session_factory(base_class=MockSession)
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("login", "user", "password"),
        ] + self._expected_session_calls_for_encoding_handling(None, "")

    def test_different_port(self):
        """
        Test setting the command channel port with `port`.
        """
        factory = ftputil.session.session_factory(base_class=MockSession, port=2121)
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 2121),
            ("login", "user", "password"),
        ] + self._expected_session_calls_for_encoding_handling(None, "")

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
        ] + self._expected_session_calls_for_encoding_handling(None, "")
        # Active mode
        factory = ftputil.session.session_factory(
            base_class=MockSession, use_passive_mode=False
        )
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("login", "user", "password"),
            ("set_pasv", False),
        ] + self._expected_session_calls_for_encoding_handling(None, "")

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
        ] + self._expected_session_calls_for_encoding_handling(None, "")
        #
        factory = ftputil.session.session_factory(
            base_class=EncryptedMockSession, encrypt_data_channel=True
        )
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("login", "user", "password"),
            ("prot_p",),
        ] + self._expected_session_calls_for_encoding_handling(None, "")
        # Without encrypted data channel.
        factory = ftputil.session.session_factory(
            base_class=EncryptedMockSession, encrypt_data_channel=False
        )
        session = factory("host", "user", "password")
        assert session.calls == [
            ("connect", "host", 21),
            ("login", "user", "password"),
        ] + self._expected_session_calls_for_encoding_handling(None, "")

    @pytest.mark.parametrize(
        "encoding, feat_command_output, expected_encoding, expected_session_calls_for_encoding_handling",
        [
            # Expected session calls for the first two tuples depend on the
            # Python version and are determined in the code below.
            #
            # For the `FEAT` command output we consider only wether the " UTF8"
            # string is present. A real `FEAT` response from a server would be
            # more complicated.
            (None, "", ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING, None),
            (
                None,
                UTF8_FEAT_STRING,
                ftputil.path_encoding.FTPLIB_DEFAULT_ENCODING,
                None,
            ),
            ("UTF-8", "", "UTF-8", [("sendcmd", "FEAT")]),
            (
                "UTF-8",
                UTF8_FEAT_STRING,
                "UTF-8",
                [("sendcmd", "FEAT"), ("sendcmd", "OPTS UTF8 ON")],
            ),
            ("latin1", "", "latin1", []),
            ("latin1", UTF8_FEAT_STRING, "latin1", []),
        ],
    )
    def test_encoding(
        self,
        encoding,
        feat_command_output,
        expected_encoding,
        expected_session_calls_for_encoding_handling,
    ):
        """
        If `encoding` has the given values, the result should be the same as
        documented.
        """
        # Special handling for default encoding.
        base_class = functools.partial(
            MockSession, feat_command_output=feat_command_output
        )
        factory = ftputil.session.session_factory(
            base_class=MockSession,
            encoding=encoding,
        )
        session = factory("host", "user", "password")
        expected_session_calls = [
            ("connect", "host", 21),
            ("login", "user", "password"),
        ] + self._expected_session_calls_for_encoding_handling(
            encoding, feat_command_output
        )
        assert session.encoding == expected_encoding

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
        ] + self._expected_session_calls_for_encoding_handling(None, "")
