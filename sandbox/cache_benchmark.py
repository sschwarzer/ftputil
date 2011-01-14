#! /usr/bin/env python
# Copyright (C) 2011, Stefan Schwarzer

import random
import sys
import time

import ftp_stat_cache


def print_statistics(task, old_time, new_time):
    """Print how long `task` (a string) took."""
    time_difference = new_time - old_time
    print "%40s took: %8.3f seconds" % (task, time_difference)


def main(max_size, new_entries):
    cache = ftp_stat_cache.StatCache()
    cache.resize(max_size)
    #cache = {}
    # Populate cache until it's full.
    t1 = time.time()
    for i in xrange(max_size):
        index = random.randint(1, max_size)
        # The cache checks if entries start with "/".
        cache["/%d" % index] = index
    t2 = time.time()
    print_statistics("Filling cache with %d entries" % max_size, t1, t2)
    # Now that the cache is full, try to add 100 more entries,
    # implicitly replacing old entries.
    for i in xrange(new_entries):
        index = random.randint(1, new_entries)
        # Make sure to add entries, not replace them.
        cache["/%d" % (max_size+index)] = index
    t3 = time.time()
    print_statistics("Replacing %d entries" % new_entries, t2, t3)


if __name__ == '__main__':
    test_size = 10000
    main(max_size=test_size, new_entries=test_size)
