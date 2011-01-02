# lrucache.py -- a simple LRU (Least-Recently-Used) cache class

# Copyright 2004 Evan Prodromou <evan@bad.dynu.ca>
# Copyright 2009-2011 Stefan Schwarzer <sschwarzer@sschwarzer.net>
#  (some changes to the original version)

# Licensed under the Academic Free License 2.1

# Licensed for ftputil under the revised BSD license
# with permission by the author, Evan Prodromou. Many
# thanks, Evan! :-)
#
# The original file is available at
# http://pypi.python.org/pypi/lrucache/0.2 .

# arch-tag: LRU cache main module

"""a simple LRU (Least-Recently-Used) cache module

This module provides very simple LRU (Least-Recently-Used) cache
functionality.

An *in-memory cache* is useful for storing the results of an
'expensive' process (one that takes a lot of time or resources) for
later re-use. Typical examples are accessing data from the filesystem,
a database, or a network location. If you know you'll need to re-read
the data again, it can help to keep it in a cache.

You *can* use a Python dictionary as a cache for some purposes.
However, if the results you're caching are large, or you have a lot of
possible results, this can be impractical memory-wise.

An *LRU cache*, on the other hand, only keeps _some_ of the results in
memory, which keeps you from overusing resources. The cache is bounded
by a maximum size; if you try to add more values to the cache, it will
automatically discard the values that you haven't read or written to
in the longest time. In other words, the least-recently-used items are
discarded. [1]_

.. [1]: 'Discarded' here means 'removed from the cache'.

"""

from __future__ import generators
import time
from heapq import heappop, heapify

# the suffix after the hyphen denotes modifications by the
#  ftputil project with respect to the original version
__version__ = "0.2-6"
__all__ = ['CacheKeyError', 'LRUCache', 'DEFAULT_SIZE']
__docformat__ = 'reStructuredText en'

DEFAULT_SIZE = 16
"""Default size of a new LRUCache object, if no 'size' argument is given."""

class CacheKeyError(KeyError):
    """Error raised when cache requests fail

    When a cache record is accessed which no longer exists (or never did),
    this error is raised. To avoid it, you may want to check for the existence
    of a cache record before reading or deleting it."""
    pass

class LRUCache(object):
    """Least-Recently-Used (LRU) cache.

    Instances of this class provide a least-recently-used (LRU) cache. They
    emulate a Python mapping type. You can use an LRU cache more or less like
    a Python dictionary, with the exception that objects you put into the
    cache may be discarded before you take them out.

    Some example usage::

    cache = LRUCache(32) # new cache
    cache['foo'] = get_file_contents('foo') # or whatever

    if 'foo' in cache: # if it's still in cache...
        # use cached version
        contents = cache['foo']
    else:
        # recalculate
        contents = get_file_contents('foo')
        # store in cache for next time
        cache['foo'] = contents

    print cache.size # Maximum size

    print len(cache) # 0 <= len(cache) <= cache.size

    cache.size = 10 # Auto-shrink on size assignment

    for i in range(50): # note: larger than cache size
        cache[i] = i

    if 0 not in cache: print 'Zero was discarded.'

    if 42 in cache:
        del cache[42] # Manual deletion

    for j in cache:   # iterate (in LRU order)
        print j, cache[j] # iterator produces keys, not values
    """

    class __Node(object):
        """Record of a cached value. Not for public consumption."""

        def __init__(self, key, obj, timestamp, sort_key):
            object.__init__(self)
            self.key = key
            self.obj = obj
            self.atime = timestamp
            self.mtime = self.atime
            self._sort_key = sort_key

        def __lt__(self, other):
            # Seems to be preferred over `__cmp__`, at least in newer
            #  Python versions. Uses only around 60 % of the time
            #  with respect to `__cmp__`.
            return self._sort_key < other._sort_key

        def __cmp__(self, other):
            return cmp(self._sort_key, other._sort_key)

        def __repr__(self):
            return "<%s %s => %s (%s)>" % \
                   (self.__class__, self.key, self.obj, \
                    time.asctime(time.localtime(self.atime)))

    def __init__(self, size=DEFAULT_SIZE):
        object.__init__(self)
        self.clear()
        """Maximum size of the cache.
        If more than 'size' elements are added to the cache,
        the least-recently-used ones will be discarded."""
        # Implicitly check size value.
        self.size = size
        self.__counter = 0

    def clear(self):
        """Clear the cache, removing all elements.
        
        The `size` attribute of the cache isn't modified.
        """
        # pylint: disable=W0201
        self.__heap = []
        self.__dict = {}

    def _sort_key(self):
        """Return a new integer value upon every call.

        Cache nodes need a monotonically increasing time indicator.
        time.time() and time.clock() don't guarantee this in a
        platform-independent way.
        """
        self.__counter += 1
        return self.__counter

    def __len__(self):
        return len(self.__heap)

    def __contains__(self, key):
        return self.__dict.has_key(key)

    def __setitem__(self, key, obj):
        if self.size == 0:
            # can't store anything
            return
        if self.__dict.has_key(key):
            node = self.__dict[key]
            # update node object in-place
            node.obj = obj
            node.atime = time.time()
            node.mtime = node.atime
            node._sort_key = self._sort_key()
        else:
            # size of the heap can be at most the value of
            #  self.size because __setattr__ decreases the cache
            #  size if the new size value is smaller; so we don't
            #  need a loop _here_
            if len(self.__heap) == self.size:
                heapify(self.__heap)
                lru = heappop(self.__heap)
                del self.__dict[lru.key]
            node = self.__Node(key, obj, time.time(), self._sort_key())
            self.__dict[key] = node
            self.__heap.append(node)

    def __getitem__(self, key):
        if not self.__dict.has_key(key):
            raise CacheKeyError(key)
        else:
            node = self.__dict[key]
            # update node object in-place
            node.atime = time.time()
            node._sort_key = self._sort_key()
            return node.obj

    def __delitem__(self, key):
        if not self.__dict.has_key(key):
            raise CacheKeyError(key)
        else:
            node = self.__dict[key]
            del self.__dict[key]
            self.__heap.remove(node)
            return node.obj

    def __iter__(self):
        heapify(self.__heap)
        copy = self.__heap[:]
        while len(copy) > 0:
            node = heappop(copy)
            yield node.key
        raise StopIteration

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        # automagically shrink heap on resize
        if name == 'size':
            size = value
            if not isinstance(size, (int, long)):
                raise TypeError("cache size (%r) must be an integer" % size)
            if size <= 0:
                raise ValueError("cache size (%d) must be positive" % size)
            heapify(self.__heap)
            while len(self.__heap) > value:
                lru = heappop(self.__heap)
                del self.__dict[lru.key]

    def __repr__(self):
        return "<%s (%d elements)>" % (str(self.__class__), len(self.__heap))

    def mtime(self, key):
        """Return the last modification time for the cache record with key.
        May be useful for cache instances where the stored values can get
        'stale', such as caching file or network resource contents."""
        if not self.__dict.has_key(key):
            raise CacheKeyError(key)
        else:
            node = self.__dict[key]
            return node.mtime

if __name__ == "__main__":
    cache = LRUCache(25)
    print cache
    for i in range(50):
        cache[i] = str(i)
    print cache
    if 46 in cache:
        del cache[46]
    print cache
    cache.size = 10
    print cache
    cache[46] = '46'
    print cache
    print len(cache)
    for c in cache:
        print c
    print cache
    print cache.mtime(46)
    for c in cache:
        print c
