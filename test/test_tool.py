# Copyright (C) 2013, Stefan Schwarzer
# See the file LICENSE for licensing terms.

from __future__ import unicode_literals

import unittest

import ftputil.compat as compat
import ftputil.tool


class TestSameStringTypeAs(unittest.TestCase):

    # The first check for equality is enough for Python 3, where
    # comparing a byte string and unicode string would raise an
    # exception. However, we need the second test for Python 2.

    def test_to_bytes_type(self):
        result = ftputil.tool.same_string_type_as(b"abc", "def")
        self.assertEqual(result, b"def")
        self.assertTrue(isinstance(result, compat.bytes_type))

    def test_to_unicode_type(self):
        result = ftputil.tool.same_string_type_as("abc", b"def")
        self.assertEqual(result, "def")
        self.assertTrue(isinstance(result, compat.unicode_type))

    def test_both_byte_type(self):
        result = ftputil.tool.same_string_type_as(b"abc", b"def")
        self.assertEqual(result, b"def")
        self.assertTrue(isinstance(result, compat.bytes_type))

    def test_both_unicode_type(self):
        result = ftputil.tool.same_string_type_as("abc", "def")
        self.assertEqual(result, "def")
        self.assertTrue(isinstance(result, compat.unicode_type))


class TestSimpleConversions(unittest.TestCase):

    def test_to_bytes_type(self):
        result = ftputil.tool.to_bytes_type(b"abc")
        self.assertEqual(result, b"abc")
        self.assertTrue(isinstance(result, compat.bytes_type))
        result = ftputil.tool.to_bytes_type("abc")
        self.assertEqual(result, b"abc")
        self.assertTrue(isinstance(result, compat.bytes_type))
        
    def test_to_unicode_type(self):
        result = ftputil.tool.to_unicode_type(b"abc")
        self.assertEqual(result, "abc")
        self.assertTrue(isinstance(result, compat.unicode_type))
        result = ftputil.tool.to_unicode_type("abc")
        self.assertEqual(result, "abc")
        self.assertTrue(isinstance(result, compat.unicode_type))


if __name__ == "__main__":
    unittest.main()
