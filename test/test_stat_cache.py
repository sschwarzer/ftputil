# Copyright (C) 2006-2018, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import time

import pytest

import ftputil.error
import ftputil.stat_cache

from test import scripted_session
from test import test_base


Call = scripted_session.Call


class TestStatCache:
    def setup_method(self, method):
        self.cache = ftputil.stat_cache.StatCache()

    def test_get_set(self):
        with pytest.raises(ftputil.error.CacheMissError):
            self.cache.__getitem__("/path")
        self.cache["/path"] = "test"
        assert self.cache["/path"] == "test"

    def test_invalidate(self):
        # Don't raise a `CacheMissError` for missing paths
        self.cache.invalidate("/path")
        self.cache["/path"] = "test"
        self.cache.invalidate("/path")
        assert len(self.cache) == 0

    def test_clear(self):
        self.cache["/path1"] = "test1"
        self.cache["/path2"] = "test2"
        self.cache.clear()
        assert len(self.cache) == 0

    def test_contains(self):
        self.cache["/path1"] = "test1"
        assert "/path1" in self.cache
        assert "/path2" not in self.cache

    def test_len(self):
        assert len(self.cache) == 0
        self.cache["/path1"] = "test1"
        self.cache["/path2"] = "test2"
        assert len(self.cache) == 2

    def test_resize(self):
        self.cache.resize(100)
        # Don't grow the cache beyond it's set size.
        for i in range(150):
            self.cache["/{0:d}".format(i)] = i
        assert len(self.cache) == 100

    def test_max_age1(self):
        """
        Set expiration after setting a cache item.
        """
        self.cache["/path1"] = "test1"
        # Expire after one second
        self.cache.max_age = 1
        time.sleep(0.5)
        # Should still be present
        assert self.cache["/path1"] == "test1"
        time.sleep(0.6)
        # Should have expired (_setting_ the cache counts)
        with pytest.raises(ftputil.error.CacheMissError):
            self.cache.__getitem__("/path1")

    def test_max_age2(self):
        """
        Set expiration before setting a cache item.
        """
        # Expire after one second
        self.cache.max_age = 1
        self.cache["/path1"] = "test1"
        time.sleep(0.5)
        # Should still be present
        assert self.cache["/path1"] == "test1"
        time.sleep(0.6)
        # Should have expired (_setting_ the cache counts)
        with pytest.raises(ftputil.error.CacheMissError):
            self.cache.__getitem__("/path1")

    def test_disabled(self):
        self.cache["/path1"] = "test1"
        self.cache.disable()
        self.cache["/path2"] = "test2"
        with pytest.raises(ftputil.error.CacheMissError):
            self.cache.__getitem__("/path1")
        with pytest.raises(ftputil.error.CacheMissError):
            self.cache.__getitem__("/path2")
        assert len(self.cache) == 1
        # Don't raise a `CacheMissError` for missing paths.
        self.cache.invalidate("/path2")

    def test_cache_size_zero(self):
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result="drwxr-sr-x   2 45854   200    512 Jan  3 17:17 download\n"
                "drwxr-sr-x   2 45854   200    512 Jul 30 17:14 dir with spaces\n"
                "lrwxrwxrwx   2 45854   200      6 May 29  2000 link -> ../link_target\n"
                "-rw-r--r--   1 45854   200   4604 Jan 19 23:11 index.html",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with pytest.raises(ValueError):
                host.stat_cache.resize(0)
            # If bug #38 was present, this would raise an `IndexError`.
            items = host.listdir(host.curdir)
            assert items == ["download", "dir with spaces", "link", "index.html"]
