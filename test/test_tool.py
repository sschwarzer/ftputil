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


class TestSameStringTypeAs:
    @staticmethod
    def _test_string_and_pathlike_object(type_source, path, expected_result):
        """
        Check if the results from `tool.same_string_type_as(type_source, path)`
        and `tool.same_string_type_as(Path(type_source), path)` both are the
        same as `expected_result`.

        `Path(type_source)` means that the type source string is wrapped in a
        `PathLike` object whose `__fspath__` method returns `type_source`.

        `type_source` must be a `bytes` or `str` object or a `PathLike` object.
        """
        result = ftputil.tool.same_string_type_as(type_source, path)
        assert result == expected_result
        result = ftputil.tool.same_string_type_as(Path(type_source), path)
        assert result == expected_result

    def test_to_bytes(self):
        self._test_string_and_pathlike_object(b"abc", "def", expected_result=b"def")

    def test_to_str(self):
        self._test_string_and_pathlike_object("abc", b"def", expected_result="def")

    def test_both_bytes_type(self):
        self._test_string_and_pathlike_object(b"abc", b"def", expected_result=b"def")

    def test_both_str_type(self):
        self._test_string_and_pathlike_object("abc", "def", expected_result="def")


as_bytes = ftputil.tool.as_bytes


class TestAsBytes:
    def test_from_bytes(self):
        assert as_bytes(b"abc") == b"abc"

    def test_from_str(self):
        assert as_bytes("abc") == b"abc"

    def test_from_bytes_path(self):
        assert as_bytes(Path(b"abc")) == b"abc"

    def test_from_str_path(self):
        assert as_bytes(Path("abc")) == b"abc"

    def test_type_error(self):
        with pytest.raises(TypeError):
            as_bytes(1)


as_str = ftputil.tool.as_str


class TestAsStr:
    def test_from_bytes(self):
        assert as_str(b"abc") == "abc"

    def test_from_str(self):
        assert as_str("abc") == "abc"

    def test_from_bytes_path(self):
        assert as_str(Path(b"abc")) == "abc"

    def test_from_str_path(self):
        assert as_str(Path("abc")) == "abc"

    def test_type_error(self):
        with pytest.raises(TypeError):
            as_str(1)
