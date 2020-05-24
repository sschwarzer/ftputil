# Copyright (C) 2013-2020, Stefan Schwarzer
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import os

import pytest

import ftputil.tool


class Path(os.PathLike):
    """
    Helper class for `TestSameStringTypeAs`
    """

    def __init__(self, type_source):
        self._type_source = type_source

    def __fspath__(self):
        return self._type_source


same_string_type_as = ftputil.tool.same_string_type_as


class TestSameStringTypeAs:
    @staticmethod
    def _test_string(type_source, string, expected_result):
        """
        Check if the result from `tool.same_string_type_as(type_source,
        string)` is the same as `expected_result`.

        `type_source` must be a `bytes` or `str` object.
        """
        result = ftputil.tool.same_string_type_as(type_source, path)
        assert result == expected_result

    def test_to_bytes(self):
        assert same_string_type_as(b"abc", "def") == b"def"

    def test_to_str(self):
        assert same_string_type_as("abc", b"def") == "def"

    def test_both_bytes_type(self):
        assert same_string_type_as(b"abc", b"def") == b"def"

    def test_both_str_type(self):
        assert same_string_type_as("abc", "def") == "def"


as_str = ftputil.tool.as_str
as_str_path = ftputil.tool.as_str_path


class TestAsStr:
    def test_from_bytes(self):
        assert as_str(b"abc") == "abc"
        assert as_str_path(b"abc") == "abc"

    def test_from_str(self):
        assert as_str("abc") == "abc"
        assert as_str_path("abc") == "abc"

    def test_from_bytes_path(self):
        assert as_str_path(Path(b"abc")) == "abc"

    def test_from_str_path(self):
        assert as_str_path(Path("abc")) == "abc"

    def test_type_error(self):
        with pytest.raises(TypeError):
            as_str(1)
