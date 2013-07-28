# encoding: utf-8
# Copyright (C) 2006-2013, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# See the file LICENSE for licensing terms.

import time
import unittest

import ftputil.error
import ftputil.stat_cache

from test import test_base


class TestStatCache(unittest.TestCase):

    def setUp(self):
        self.cache = ftputil.stat_cache.StatCache()

    def test_get_set(self):
        self.assertRaises(ftputil.error.CacheMissError,
                          self.cache.__getitem__, "/path")
        self.cache["/path"] = "test"
        self.assertEqual(self.cache["/path"], "test")

    def test_invalidate(self):
        # Don't raise a `CacheMissError` for missing paths
        self.cache.invalidate("/path")
        self.cache["/path"] = "test"
        self.cache.invalidate("/path")
        self.assertEqual(len(self.cache), 0)

    def test_clear(self):
        self.cache["/path1"] = "test1"
        self.cache["/path2"] = "test2"
        self.cache.clear()
        self.assertEqual(len(self.cache), 0)

    def test_contains(self):
        self.cache["/path1"] = "test1"
        self.assertTrue ("/path1" in self.cache)
        self.assertFalse("/path2" in self.cache)

    def test_len(self):
        self.assertEqual(len(self.cache), 0)
        self.cache["/path1"] = "test1"
        self.cache["/path2"] = "test2"
        self.assertEqual(len(self.cache), 2)

    def test_resize(self):
        self.cache.resize(100)
        # Don't grow the cache beyond it's set size.
        for i in range(150):
            self.cache["/{0:d}".format(i)] = i
        self.assertEqual(len(self.cache), 100)

    def test_max_age1(self):
        """Set expiration after setting a cache item."""
        self.cache["/path1"] = "test1"
        # Expire after one second
        self.cache.max_age = 1
        time.sleep(0.5)
        # Should still be present
        self.assertEqual(self.cache["/path1"], "test1")
        time.sleep(0.6)
        # Should have expired (_setting_ the cache counts)
        self.assertRaises(ftputil.error.CacheMissError,
                          self.cache.__getitem__, "/path1")

    def test_max_age2(self):
        """Set expiration before setting a cache item."""
        # Expire after one second
        self.cache.max_age = 1
        self.cache["/path1"] = "test1"
        time.sleep(0.5)
        # Should still be present
        self.assertEqual(self.cache["/path1"], "test1")
        time.sleep(0.6)
        # Should have expired (_setting_ the cache counts)
        self.assertRaises(ftputil.error.CacheMissError,
                          self.cache.__getitem__, "/path1")

    def test_disabled(self):
        self.cache["/path1"] = "test1"
        self.cache.disable()
        self.cache["/path2"] = "test2"
        self.assertRaises(ftputil.error.CacheMissError,
                          self.cache.__getitem__, "/path1")
        self.assertRaises(ftputil.error.CacheMissError,
                          self.cache.__getitem__, "/path2")
        self.assertEqual(len(self.cache), 1)
        # Don't raise a `CacheMissError` for missing paths
        self.cache.invalidate("/path2")

    def test_cache_size_zero(self):
        host = test_base.ftp_host_factory()
        self.assertRaises(ValueError, host.stat_cache.resize, 0)
        # If bug #38 is present, this raises an `IndexError`.
        items = host.listdir(host.curdir)
        self.assertEqual(items[:3], ['chemeng', 'download', 'image'])

    #
    # Tests of implicit decoding of paths.
    # Idea: The cache entry for corresponding unicode and bytes
    # versions of paths should be aliased.
    #
    def _umlaut_paths(self):
        """Return a unicode and a bytes version of a path with umlaut."""
        unicode_path = "/path_ä"
        bytes_path = ftputil.tool.as_bytes(unicode_path)
        return unicode_path, bytes_path

    def test_implicit_decoding_for_setitem(self):
        """Test whether a bytes argument for `__setitem__` is decoded."""
        unicode_path, bytes_path = self._umlaut_paths()
        self.cache[bytes_path] = "test"
        self.assertEqual(self.cache[unicode_path], "test")

    def test_implicit_decoding_for_getitem(self):
        """Test whether a bytes argument for `__getitem__` is decoded."""
        unicode_path, bytes_path = self._umlaut_paths()
        self.cache[unicode_path] = "test"
        self.assertEqual(self.cache[bytes_path], "test")

    def test_implicit_decoding_for_invalidate(self):
        """Test whether a bytes argument for `invalidate` is decoded."""
        unicode_path, bytes_path = self._umlaut_paths()
        self.cache[unicode_path] = "test"
        self.cache.invalidate(bytes_path)
        self.assertEqual(len(self.cache), 0)

    def test_implicit_decoding_for_contains(self):
        """Test whether a bytes argument for `__contains__` is decoded."""
        unicode_path, bytes_path = self._umlaut_paths()
        self.cache[unicode_path] = "test"
        self.assertTrue(bytes_path in self.cache)


if __name__ == '__main__':
    unittest.main()
