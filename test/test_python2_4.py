# Copyright (C) 2003-2013, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# See the file LICENSE for licensing terms.

import unittest

import ftputil.error


class Python24(unittest.TestCase):
    """Test for faults which occur only with Python 2.4 (possibly below)."""

    def test_exception_base_class(self):
        try:
            raise ftputil.error.FTPOSError("")
        except TypeError:
            self.fail("can't use super in classic class")
        except ftputil.error.FTPOSError:
            # Everything's fine
            pass


if __name__ == '__main__':
    unittest.main()
