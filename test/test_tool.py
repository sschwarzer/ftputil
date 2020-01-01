# Copyright (C) 2013-2018, Stefan Schwarzer
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import os

import ftputil.tool


class TypeSourcePath(os.PathLike):
    """
    Helper class for `TestSameStringTypeAs`
    """

    def __init__(self, type_source):
        self._type_source = type_source

    def __fspath__(self):
        return self._type_source


class TestSameStringTypeAs:
    @staticmethod
    def _test_string_and_pathlike_object(type_source, content_source, expected_result):
        """
        Check if the results from
        `tool.same_string_type_as(type_source, content_source)` and
        `tool.same_string_type_as(TypeSourcePath(type_source), content_source)`
        both are the same as `expected_result`.

        `TypeSourcePath(type_source)` means that the type source
        string is wrapped in a `PathLike` object whose `__fspath__`
        method returns `type_source`.

        `type_source` must be a unicode string or byte string.
        """
        result = ftputil.tool.same_string_type_as(type_source, content_source)
        assert result == expected_result
        #
        type_source = TypeSourcePath(type_source)
        result = ftputil.tool.same_string_type_as(type_source, content_source)
        assert result == expected_result

    def test_to_bytes(self):
        self._test_string_and_pathlike_object(b"abc", "def", expected_result=b"def")

    def test_to_str(self):
        self._test_string_and_pathlike_object("abc", b"def", expected_result="def")

    def test_both_bytes_type(self):
        self._test_string_and_pathlike_object(b"abc", b"def", expected_result=b"def")

    def test_both_str_type(self):
        self._test_string_and_pathlike_object("abc", "def", expected_result="def")


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
