# Copyright (C) 2003-2019, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import datetime
import ftplib
import stat
import time

import freezegun
import pytest

import ftputil
import ftputil.error
import ftputil.stat
from ftputil.stat import MINUTE_PRECISION, DAY_PRECISION, UNKNOWN_PRECISION

from test import test_base
from test import scripted_session


Call = scripted_session.Call


# Special value to handle special case of datetimes before the epoch.
EPOCH = time.gmtime(0)[:6]


def stat_tuple_to_seconds(t):
    """
    Return a float number representing the UTC timestamp from the six-element
    tuple `t`.
    """
    assert len(t) == 6, "need a six-element tuple (year, month, day, hour, min, sec)"
    # Do _not_ apply `time.mktime` to the `EPOCH` value below. On some
    # platforms (e. g. Windows) this might cause an `OverflowError`.
    if t == EPOCH:
        return 0.0
    else:
        return datetime.datetime(*t, tzinfo=datetime.timezone.utc).timestamp()


class TestParsers:

    #
    # Helper methods
    #
    def _test_valid_lines(self, parser_class, lines, expected_stat_results):
        parser = parser_class()
        for line, expected_stat_result in zip(lines, expected_stat_results):
            # Convert to list to compare with the list `expected_stat_results`.
            parse_result = parser.parse_line(line, time_shift=5 * 60 * 60)
            stat_result = list(parse_result) + [
                parse_result._st_mtime_precision,
                parse_result._st_name,
                parse_result._st_target,
            ]
            # Convert time tuple to seconds.
            expected_stat_result[8] = stat_tuple_to_seconds(expected_stat_result[8])
            # Compare lists.
            assert stat_result == expected_stat_result

    def _test_invalid_lines(self, parser_class, lines):
        parser = parser_class()
        for line in lines:
            with pytest.raises(ftputil.error.ParserError):
                parser.parse_line(line)

    def _expected_year(self):
        """
        Return the expected year for the second line in the listing in
        `test_valid_unix_lines`.
        """
        # If in this year it's after Dec 19, 23:11, use the current year, else
        # use the previous year. This datetime value corresponds to the
        # hard-coded value in the string lists below.
        client_datetime = datetime.datetime.now(datetime.timezone.utc)
        server_datetime_candidate = client_datetime.replace(
            month=12, day=19, hour=23, minute=11, second=0
        )
        if server_datetime_candidate > client_datetime:
            return server_datetime_candidate.year - 1
        else:
            return server_datetime_candidate.year

    #
    # Unix parser
    #
    def test_valid_unix_lines(self):
        lines = [
            "drwxr-sr-x   2 45854    200           512 May  4  2000 "
            "chemeng link -> chemeng target",
            # The year value for this line will change with the actual time.
            "-rw-r--r--   1 45854    200          4604 Dec 19 23:11 index.html",
            "drwxr-sr-x   2 45854    200           512 Jan 01  2000 os2",
            "----------   2 45854    200           512 May 29  2000 some_file",
            "lrwxrwxrwx   2 45854    200           512 May 29  2000 osup -> " "../os2",
        ]
        # Note that the time shift is also subtracted from the datetimes that
        # have only day precision, i. e. a year but no time.
        expected_stat_results = [
            [
                17901,
                None,
                None,
                2,
                "45854",
                "200",
                512,
                None,
                (2000, 5, 3, 19, 0, 0),
                None,
                DAY_PRECISION,
                "chemeng link",
                "chemeng target",
            ],
            [
                33188,
                None,
                None,
                1,
                "45854",
                "200",
                4604,
                None,
                (self._expected_year(), 12, 19, 18, 11, 0),
                None,
                MINUTE_PRECISION,
                "index.html",
                None,
            ],
            [
                17901,
                None,
                None,
                2,
                "45854",
                "200",
                512,
                None,
                (1999, 12, 31, 19, 0, 0),
                None,
                DAY_PRECISION,
                "os2",
                None,
            ],
            [
                32768,
                None,
                None,
                2,
                "45854",
                "200",
                512,
                None,
                (2000, 5, 28, 19, 0, 0),
                None,
                DAY_PRECISION,
                "some_file",
                None,
            ],
            [
                41471,
                None,
                None,
                2,
                "45854",
                "200",
                512,
                None,
                (2000, 5, 28, 19, 0, 0),
                None,
                DAY_PRECISION,
                "osup",
                "../os2",
            ],
        ]
        self._test_valid_lines(ftputil.stat.UnixParser, lines, expected_stat_results)

    def test_alternative_unix_format(self):
        # See http://ftputil.sschwarzer.net/trac/ticket/12 for a description
        # for the need for an alternative format.
        lines = [
            "drwxr-sr-x   2   200           512 May  4  2000 "
            "chemeng link -> chemeng target",
            # The year value for this line will change with the actual time.
            "-rw-r--r--   1   200          4604 Dec 19 23:11 index.html",
            "drwxr-sr-x   2   200           512 May 29  2000 os2",
            "lrwxrwxrwx   2   200           512 May 29  2000 osup -> ../os2",
        ]
        expected_stat_results = [
            [
                17901,
                None,
                None,
                2,
                None,
                "200",
                512,
                None,
                (2000, 5, 3, 19, 0, 0),
                None,
                DAY_PRECISION,
                "chemeng link",
                "chemeng target",
            ],
            [
                33188,
                None,
                None,
                1,
                None,
                "200",
                4604,
                None,
                (self._expected_year(), 12, 19, 18, 11, 0),
                None,
                MINUTE_PRECISION,
                "index.html",
                None,
            ],
            [
                17901,
                None,
                None,
                2,
                None,
                "200",
                512,
                None,
                (2000, 5, 28, 19, 0, 0),
                None,
                DAY_PRECISION,
                "os2",
                None,
            ],
            [
                41471,
                None,
                None,
                2,
                None,
                "200",
                512,
                None,
                (2000, 5, 28, 19, 0, 0),
                None,
                DAY_PRECISION,
                "osup",
                "../os2",
            ],
        ]
        self._test_valid_lines(ftputil.stat.UnixParser, lines, expected_stat_results)

    def test_pre_epoch_times_for_unix(self):
        # See http://ftputil.sschwarzer.net/trac/ticket/83 .
        # `mirrors.ibiblio.org` returns dates before the "epoch" that cause an
        # `OverflowError` in `mktime` on some platforms, e. g. Windows.
        lines = [
            "-rw-r--r--   1 45854    200          4604 May  4  1968 index.html",
            "-rw-r--r--   1 45854    200          4604 Dec 31  1969 index.html",
            "-rw-r--r--   1 45854    200          4604 May  4  1800 index.html",
        ]
        expected_stat_result = [
            33188,
            None,
            None,
            1,
            "45854",
            "200",
            4604,
            None,
            EPOCH,
            None,
            UNKNOWN_PRECISION,
            "index.html",
            None,
        ]
        # Make shallow copies to avoid converting the time tuple more than once
        # in _test_valid_lines`.
        expected_stat_results = [
            expected_stat_result[:],
            expected_stat_result[:],
            expected_stat_result[:],
        ]
        self._test_valid_lines(ftputil.stat.UnixParser, lines, expected_stat_results)

    def test_invalid_unix_lines(self):
        lines = [
            # Not intended to be parsed. Should have been filtered out by
            # `ignores_line`.
            "total 14",
            # Invalid month abbreviation
            "drwxr-sr-x   2 45854    200           512 Max  4  2000 chemeng",
            # Year value isn't an integer
            "drwxr-sr-x   2 45854    200           512 May  4  abcd chemeng",
            # Day value isn't an integer
            "drwxr-sr-x   2 45854    200           512 May ab  2000 chemeng",
            # Hour value isn't an integer
            "-rw-r--r--   1 45854    200          4604 Dec 19 ab:11 index.html",
            # Minute value isn't an integer
            "-rw-r--r--   1 45854    200          4604 Dec 19 23:ab index.html",
            # Day value too large
            "drwxr-sr-x   2 45854    200           512 May 32  2000 chemeng",
            # Ditto, for time instead of year
            "drwxr-sr-x   2 45854    200           512 May 32 11:22 chemeng",
            # Incomplete mode
            "drwxr-sr-    2 45854    200           512 May  4  2000 chemeng",
            # Invalid first letter in mode
            "xrwxr-sr-x   2 45854    200           512 May  4  2000 chemeng",
            # Ditto, plus invalid size value
            "xrwxr-sr-x   2 45854    200           51x May  4  2000 chemeng",
            # Is this `os1 -> os2` pointing to `os3`, or `os1` pointing to
            # `os2 -> os3` or the plain name `os1 -> os2 -> os3`? We don't
            # know, so we consider the line invalid.
            "drwxr-sr-x   2 45854    200           512 May 29  2000 "
            "os1 -> os2 -> os3",
            # Missing name
            "-rwxr-sr-x   2 45854    200           51x May  4  2000 ",
        ]
        self._test_invalid_lines(ftputil.stat.UnixParser, lines)

    #
    # Microsoft parser
    #
    def test_valid_ms_lines_two_digit_year(self):
        lines = [
            "07-27-01  11:16AM       <DIR>          Test",
            "10-23-95  03:25PM       <DIR>          WindowsXP",
            "07-17-00  02:08PM             12266720 test.exe",
            "07-17-09  12:08AM             12266720 test.exe",
            "07-17-09  12:08PM             12266720 test.exe",
        ]
        expected_stat_results = [
            [
                16640,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                (2001, 7, 27, 6, 16, 0),
                None,
                MINUTE_PRECISION,
                "Test",
                None,
            ],
            [
                16640,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                (1995, 10, 23, 10, 25, 0),
                None,
                MINUTE_PRECISION,
                "WindowsXP",
                None,
            ],
            [
                33024,
                None,
                None,
                None,
                None,
                None,
                12266720,
                None,
                (2000, 7, 17, 9, 8, 0),
                None,
                MINUTE_PRECISION,
                "test.exe",
                None,
            ],
            [
                33024,
                None,
                None,
                None,
                None,
                None,
                12266720,
                None,
                (2009, 7, 16, 19, 8, 0),
                None,
                MINUTE_PRECISION,
                "test.exe",
                None,
            ],
            [
                33024,
                None,
                None,
                None,
                None,
                None,
                12266720,
                None,
                (2009, 7, 17, 7, 8, 0),
                None,
                MINUTE_PRECISION,
                "test.exe",
                None,
            ],
        ]
        self._test_valid_lines(ftputil.stat.MSParser, lines, expected_stat_results)

    def test_valid_ms_lines_four_digit_year(self):
        # See http://ftputil.sschwarzer.net/trac/ticket/67
        lines = [
            "10-19-2012  03:13PM       <DIR>          SYNCDEST",
            "10-19-2012  03:13PM       <DIR>          SYNCSOURCE",
            "10-19-1968  03:13PM       <DIR>          SYNC",
        ]
        expected_stat_results = [
            [
                16640,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                (2012, 10, 19, 10, 13, 0),
                None,
                MINUTE_PRECISION,
                "SYNCDEST",
                None,
            ],
            [
                16640,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                (2012, 10, 19, 10, 13, 0),
                None,
                MINUTE_PRECISION,
                "SYNCSOURCE",
                None,
            ],
            [
                16640,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                EPOCH,
                None,
                UNKNOWN_PRECISION,
                "SYNC",
                None,
            ],
        ]
        self._test_valid_lines(ftputil.stat.MSParser, lines, expected_stat_results)

    def test_invalid_ms_lines(self):
        lines = [
            # Neither "<DIR>" nor a size present
            "07-27-01  11:16AM                      Test",
            # "AM"/"PM" missing
            "07-17-00  02:08             12266720 test.exe",
            # Year not an int
            "07-17-ab  02:08AM           12266720 test.exe",
            # Month not an int
            "ab-17-00  02:08AM           12266720 test.exe",
            # Day not an int
            "07-ab-00  02:08AM           12266720 test.exe",
            # Hour not an int
            "07-17-00  ab:08AM           12266720 test.exe",
            # Invalid size value
            "07-17-00  02:08AM           1226672x test.exe",
        ]
        self._test_invalid_lines(ftputil.stat.MSParser, lines)

    #
    # The following code checks if the decision logic in the Unix line parser
    # for determining the year works.
    #
    def dir_line(self, datetime_):
        """
        Return a directory line as from a Unix FTP server. Most of the contents
        are fixed, but the timestamp is made from `time_float` (seconds since
        the epoch, as from `time.time()`).
        """
        line_template = "-rw-r--r--   1   45854   200   4604   {}   index.html"
        datetime_string = datetime_.strftime("%b %d %H:%M")
        return line_template.format(datetime_string)

    def assert_equal_times(self, time1, time2):
        """
        Check if both times (seconds since the epoch) are equal. For the
        purpose of this test, two times are "equal" if they differ no more than
        one minute from each other.
        """
        abs_difference = abs(time1 - time2)
        assert abs_difference <= 60.0, "Difference is %s seconds" % abs_difference

    def _test_time_shift(self, supposed_time_shift, deviation=0.0):
        """
        Check if the stat parser considers the time shift value correctly.
        `deviation` is the difference between the actual time shift and the
        supposed time shift, which is rounded to full hours.
        """
        script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            # Explicitly use Unix format parser here.
            host._stat._parser = ftputil.stat.UnixParser()
            host.set_time_shift(supposed_time_shift)
            server_time = datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(seconds=supposed_time_shift + deviation)
            stat_result = host._stat._parser.parse_line(
                self.dir_line(server_time), host.time_shift()
            )
            # We expect `st_mtime` in UTC.
            self.assert_equal_times(
                stat_result.st_mtime,
                (
                    server_time
                    # Convert back to client time.
                    - datetime.timedelta(seconds=supposed_time_shift)
                ).timestamp(),
            )

    def test_time_shifts(self):
        """
        Test correct year depending on time shift value.
        """
        # 1. test: Client and server share the same time (UTC). This is true if
        # the directory listing from the server is in UTC.
        self._test_time_shift(0.0)
        # 2. test: Server is three hours ahead of client
        self._test_time_shift(3 * 60 * 60)
        # Ditto, but with client and server in different years. See ticket #131.
        with freezegun.freeze_time("2019-12-31 22:37"):
            self._test_time_shift(3 * 60 * 60)
        # 3. test: Client is three hours ahead of server
        self._test_time_shift(-3 * 60 * 60)
        # 4. test: Server is supposed to be three hours ahead, but is ahead
        # three hours and one minute
        self._test_time_shift(3 * 60 * 60, 60)
        # 5. test: Server is supposed to be three hours ahead, but is ahead
        # three hours minus one minute
        self._test_time_shift(3 * 60 * 60, -60)
        # 6. test: Client is supposed to be three hours ahead, but is ahead
        # three hours and one minute
        self._test_time_shift(-3 * 60 * 60, -60)
        # 7. test: Client is supposed to be three hours ahead, but is ahead
        # three hours minus one minute
        self._test_time_shift(-3 * 60 * 60, 60)


class TestLstatAndStat:
    """
    Test `FTPHost.lstat` and `FTPHost.stat` (test currently only implemented
    for Unix server format).
    """

    def test_repr(self):
        """
        Test if the `repr` result looks like a named tuple.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result="drwxr-sr-x   2 45854   200   512 May  4  2000 foo",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            stat_result = host.stat("/foo")
            expected_result = (
                "StatResult(st_mode=17901, st_ino=None, st_dev=None, "
                "st_nlink=2, st_uid='45854', st_gid='200', st_size=512, "
                "st_atime=None, st_mtime=957398400.0, st_ctime=None)"
            )
            assert repr(stat_result) == expected_result

    def test_failing_lstat(self):
        """
        Test whether `lstat` fails for a nonexistent path.
        """
        # Directory with presumed file item doesn't exist.
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            # See FIXME comment in `ftputil.stat._Stat._real_lstat`
            Call("cwd", args=("/",)),
            Call("cwd", args=("/notthere",), result=ftplib.error_perm),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            with pytest.raises(ftputil.error.PermanentError):
                host.lstat("/notthere/irrelevant")
        # Directory exists, but not the file system item in the directory.
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result=test_base.dir_line(
                    mode_string="dr-xr-xr-x",
                    datetime_=datetime.datetime.now(),
                    name="some_dir",
                ),
            ),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/some_dir",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            with pytest.raises(ftputil.error.PermanentError):
                host.lstat("/some_dir/notthere")

    def test_lstat_for_root(self):
        """
        Test `lstat` for `/` .

        Note: `(l)stat` works by going one directory up and parsing the output
        of an FTP `LIST` command. Unfortunately, it's not possible to do this
        for the root directory `/`.
        """
        script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            with pytest.raises(ftputil.error.RootDirError) as exc_info:
                host.lstat("/")
        # `RootDirError` is "outside" the `FTPOSError` hierarchy.
        assert not isinstance(exc_info.value, ftputil.error.FTPOSError)
        del exc_info

    def test_lstat_one_unix_file(self):
        """
        Test `lstat` for a file described in Unix-style format.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result="-rw-r--r--   1 45854   200   4604 Jan 19 23:11 some_file",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            stat_result = host.lstat("/some_file")
        assert oct(stat_result.st_mode) == "0o100644"
        assert stat_result.st_size == 4604
        assert stat_result._st_mtime_precision == 60

    def test_lstat_one_ms_file(self):
        """
        Test `lstat` for a file described in DOS-style format.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # First try with unix parser, but this parser can't parse this
            # line.
            Call(
                "dir",
                args=("",),
                result="07-17-00  02:08PM             12266720 some_file",
            ),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # Now try with MS parser.
            Call(
                "dir",
                args=("",),
                result="07-17-00  02:08PM             12266720 some_file",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            stat_result = host.lstat("/some_file")
        assert stat_result._st_name == "some_file"
        assert stat_result._st_mtime_precision == 60

    def test_lstat_one_unix_dir(self):
        """
        Test `lstat` for a directory described in Unix-style format.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result="drwxr-sr-x   6 45854   200   512 Sep 20  1999 some_dir",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            stat_result = host.lstat("/some_dir")
        assert oct(stat_result.st_mode) == "0o42755"
        assert stat_result.st_ino is None
        assert stat_result.st_dev is None
        assert stat_result.st_nlink == 6
        assert stat_result.st_uid == "45854"
        assert stat_result.st_gid == "200"
        assert stat_result.st_size == 512
        assert stat_result.st_atime is None
        assert stat_result.st_mtime == stat_tuple_to_seconds((1999, 9, 20, 0, 0, 0))
        assert stat_result.st_ctime is None
        assert stat_result._st_mtime_precision == 24 * 60 * 60
        assert stat_result == (
            17901,
            None,
            None,
            6,
            "45854",
            "200",
            512,
            None,
            stat_tuple_to_seconds((1999, 9, 20, 0, 0, 0)),
            None,
        )

    def test_lstat_one_ms_dir(self):
        """
        Test `lstat` for a directory described in DOS-style format.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # First try with unix parser, but this parser can't parse this
            # line.
            Call(
                "dir",
                args=("",),
                result="10-23-01  03:25PM       <DIR>          some_dir",
            ),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # Now try with MS parser.
            Call(
                "dir",
                args=("",),
                result="10-23-01  03:25PM       <DIR>          some_dir",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            stat_result = host.lstat("/some_dir")
        assert stat_result._st_mtime_precision == 60

    def test_lstat_via_stat_module(self):
        """
        Test `lstat` indirectly via `stat` module.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result="drwxr-sr-x   2 45854   200   512 May  4  2000 some_dir",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            stat_result = host.lstat("/some_dir")
        assert stat.S_ISDIR(stat_result.st_mode)

    def test_stat_following_link(self):
        """
        Test `stat` when invoked on a link.
        """
        # Simple link
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result="lrwxrwxrwx   1 45854   200   21 Jan 19  2002 link -> link_target",
            ),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result="-rw-r--r--   1 45854   200   4604 Jan 19 23:11 link_target",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            stat_result = host.stat("/link")
        assert stat_result.st_size == 4604
        # Link pointing to a link
        dir_lines = (
            "lrwxrwxrwx   1 45854   200   7    Jan 19  2002 link_link -> link\n"
            "lrwxrwxrwx   1 45854   200   14   Jan 19  2002 link -> link_target\n"
            "-rw-r--r--   1 45854   200   4604 Jan 19 23:11 link_target"
        )
        # Note that only one `dir` call would be needed in case of an enabled
        # cache.
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # Look up `/link_link`.
            Call("dir", args=("",), result=dir_lines),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # Look up `/link`.
            Call("dir", args=("",), result=dir_lines),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # Look up `/link_target`.
            Call("dir", args=("",), result=dir_lines),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            stat_result = host.stat("/link_link")
        assert stat_result.st_size == 4604
        # Recursive link structure
        dir_lines = (
            "lrwxrwxrwx   1 45854   200   7    Jan 19  2002 bad_link1 -> bad_link2\n"
            "lrwxrwxrwx   1 45854   200   14   Jan 19  2002 bad_link2 -> bad_link1"
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # This dir finds the `bad_link1` name requested in the `stat` call.
            Call("dir", args=("",), result=dir_lines),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # Look up link target `bad_link2`.
            Call("dir", args=("",), result=dir_lines),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            # FIXME: `stat` looks up the link target pointed to by `bad_link2`,
            # which is `bad_link1`. Only here ftputil notices the recursive
            # link chain. Obviously the start of the link chain hadn't been
            # stored in `visited_paths` (see also ticket #108).
            Call("dir", args=("",), result=dir_lines),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            with pytest.raises(ftputil.error.PermanentError):
                host.stat("bad_link1")

    #
    # Test automatic switching of Unix/MS parsers
    #
    def test_parser_switching_with_permanent_error(self):
        """
        Test non-switching of parser format with `PermanentError`.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir", args=("",), result="10-23-01  03:25PM       <DIR>          home"
            ),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir", args=("",), result="10-23-01  03:25PM       <DIR>          home"
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert host._stat._allow_parser_switching is True
            # With these directory contents, we get a `ParserError` for the
            # Unix parser first, so `_allow_parser_switching` can be switched
            # off no matter whether we got a `PermanentError` afterward or not.
            with pytest.raises(ftputil.error.PermanentError):
                host.lstat("/nonexistent")
            assert host._stat._allow_parser_switching is False

    def test_parser_switching_default_to_unix(self):
        """
        Test non-switching of parser format; stay with Unix.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result="-rw-r--r--   1 45854   200   4604 Jan 19 23:11 some_file",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert host._stat._allow_parser_switching is True
            assert host._stat._allow_parser_switching is True
            assert isinstance(host._stat._parser, ftputil.stat.UnixParser)
            stat_result = host.lstat("some_file")
            # The Unix parser worked, so keep it.
            assert isinstance(host._stat._parser, ftputil.stat.UnixParser)
            assert host._stat._allow_parser_switching is False

    def test_parser_switching_to_ms(self):
        """
        Test switching of parser from Unix to MS format.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result="07-17-00  02:08PM             12266720 some_file",
            ),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call(
                "dir",
                args=("",),
                result="07-17-00  02:08PM             12266720 some_file",
            ),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert host._stat._allow_parser_switching is True
            assert isinstance(host._stat._parser, ftputil.stat.UnixParser)
            # Parsing the directory `/` with the Unix parser fails, so switch
            # to the MS parser.
            stat_result = host.lstat("/some_file")
            assert isinstance(host._stat._parser, ftputil.stat.MSParser)
            assert host._stat._allow_parser_switching is False
            assert stat_result._st_name == "some_file"
            assert stat_result.st_size == 12266720

    def test_parser_switching_regarding_empty_dir(self):
        """Test switching of parser if a directory is empty."""
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            assert host._stat._allow_parser_switching is True
            # When the directory we're looking into doesn't give us any lines
            # we can't decide whether the first parser worked, because it
            # wasn't applied. So keep the parser for now.
            result = host.listdir("/")
            assert result == []
            assert host._stat._allow_parser_switching is True
            assert isinstance(host._stat._parser, ftputil.stat.UnixParser)


class TestListdir:
    """
    Test `FTPHost.listdir`.
    """

    def test_failing_listdir(self):
        """
        Test failing `FTPHost.listdir`.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=""),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.stat_cache.disable()
            with pytest.raises(ftputil.error.PermanentError):
                host.listdir("notthere")

    def test_succeeding_listdir(self):
        """
        Test succeeding `FTPHost.listdir`.
        """
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
            host.stat_cache.disable()
            remote_file_list = host.listdir(".")
            # Do we have all expected "files"?
            assert len(remote_file_list) == 4
            expected_names = ["download", "dir with spaces", "link", "index.html"]
            for name in expected_names:
                assert name in remote_file_list
            assert len(host.stat_cache) == 0
