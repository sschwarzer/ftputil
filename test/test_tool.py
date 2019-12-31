# Copyright (C) 2013-2018, Stefan Schwarzer
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import ftputil.tool


class TestSameStringTypeAs:
    def test_to_bytes(self):
        result = ftputil.tool.same_string_type_as(b"abc", "def")
        assert result == b"def"

    def test_to_str(self):
        result = ftputil.tool.same_string_type_as("abc", b"def")
        assert result == "def"

    def test_both_bytes_type(self):
        result = ftputil.tool.same_string_type_as(b"abc", b"def")
        assert result == b"def"

    def test_both_str_type(self):
        result = ftputil.tool.same_string_type_as("abc", "def")
        assert result == "def"


class TestSimpleConversions:
    def test_as_bytes(self):
        result = ftputil.tool.as_bytes(b"abc")
        assert result == b"abc"
        result = ftputil.tool.as_bytes("abc")
        assert result == b"abc"

    def test_as_str(self):
        result = ftputil.tool.as_str(b"abc")
        assert result == "abc"
        result = ftputil.tool.as_str("abc")
        assert result == "abc"
