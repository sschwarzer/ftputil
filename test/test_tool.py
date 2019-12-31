# Copyright (C) 2013-2018, Stefan Schwarzer
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import ftputil.tool


class TestSameStringTypeAs:

    # The first check for equality is enough for Python 3, where
    # comparing a byte string and unicode string would raise an
    # exception. However, we need the second test for Python 2.

    def test_to_bytes(self):
        result = ftputil.tool.same_string_type_as(b"abc", "def")
        assert result == b"def"

    def test_to_unicode(self):
        result = ftputil.tool.same_string_type_as("abc", b"def")
        assert result == "def"

    def test_both_bytes_type(self):
        result = ftputil.tool.same_string_type_as(b"abc", b"def")
        assert result == b"def"

    def test_both_unicode_type(self):
        result = ftputil.tool.same_string_type_as("abc", "def")
        assert result == "def"


class TestSimpleConversions:
    def test_as_bytes(self):
        result = ftputil.tool.as_bytes(b"abc")
        assert result == b"abc"
        result = ftputil.tool.as_bytes("abc")
        assert result == b"abc"

    def test_as_unicode(self):
        result = ftputil.tool.as_str(b"abc")
        assert result == "abc"
        result = ftputil.tool.as_str("abc")
        assert result == "abc"


class TestEncodeIfUnicode:
    def test_do_encode(self):
        string = "abc"
        converted_string = ftputil.tool.encode_if_unicode(string, "latin1")
        assert converted_string == b"abc"

    def test_dont_encode(self):
        string = b"abc"
        not_converted_string = ftputil.tool.encode_if_unicode(string, "latin1")
        assert string == not_converted_string
