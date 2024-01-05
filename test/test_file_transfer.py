# Copyright (C) 2010-2020, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import datetime
import io
import random

import pytest

import ftputil.file_transfer
import ftputil.stat

from test import test_base
from test import scripted_session


Call = scripted_session.Call


class MockFile:
    """
    Class compatible with `LocalFile` and `RemoteFile`.
    """

    def __init__(self, mtime, mtime_precision):
        self._mtime = mtime
        self._mtime_precision = mtime_precision

    def mtime(self):
        return self._mtime

    def mtime_precision(self):
        return self._mtime_precision


class TestRemoteFile:
    def test_time_shift_subtracted_only_once(self):
        """
        Test whether the time shift value is subtracted from the initial server
        timestamp only once.

        This subtraction happens in `stat._Stat.parse_unix_time`, so it must
        _not_ be done a second time in `file_transfer.RemoteFile`.
        """
        utcnow = datetime.datetime.now(datetime.timezone.utc)
        # 3 hours
        time_shift = 3 * 60 * 60
        dir_line = test_base.dir_line(
            datetime_=utcnow + datetime.timedelta(seconds=time_shift), name="dummy_name"
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.set_time_shift(3 * 60 * 60)
            remote_file = ftputil.file_transfer.RemoteFile(host, "dummy_name", 0o644)
            remote_mtime = remote_file.mtime()
        # The remote mtime should be corrected by the time shift, so the
        # calculated UTC time is the same as for the client. The 60.0 (seconds)
        # is the timestamp precision.
        assert remote_mtime <= utcnow.timestamp() <= remote_mtime + 60.0


class TestTimestampComparison:
    def test_source_is_newer_than_target(self):
        """
        Test whether the source is newer than the target, i. e. if the
        file should be transferred.
        """
        # Define some time units/precisions.
        second = 1.0
        minute = 60 * second
        hour = 60 * minute
        day = 24 * hour
        unknown = ftputil.stat.UNKNOWN_PRECISION
        # Define input arguments; modification datetimes are in seconds. Fields
        # are source datetime/precision, target datetime/precision, expected
        # comparison result.
        file_data = [
            # Non-overlapping modification datetimes/precisions
            (1000.0, second, 900.0, second, True),
            (900.0, second, 1000.0, second, False),
            # Equal modification datetimes/precisions (if in doubt, transfer)
            (1000.0, second, 1000.0, second, True),
            # Just touching intervals
            (1000.0, second, 1000.0 + second, minute, True),
            (1000.0 + second, minute, 1000.0, second, True),
            # Other overlapping intervals
            (10000.0 - 0.5 * hour, hour, 10000.0, day, True),
            (10000.0 + 0.5 * hour, hour, 10000.0, day, True),
            (10000.0 + 0.2 * hour, 0.2 * hour, 10000.0, hour, True),
            (10000.0 - 0.2 * hour, 2 * hour, 10000.0, hour, True),
            # Unknown precision
            (1000.0, unknown, 1000.0, second, True),
            (1000.0, second, 1000.0, unknown, True),
            (1000.0, unknown, 1000.0, unknown, True),
        ]
        for (
            source_mtime,
            source_mtime_precision,
            target_mtime,
            target_mtime_precision,
            expected_result,
        ) in file_data:
            source_file = MockFile(source_mtime, source_mtime_precision)
            target_file = MockFile(target_mtime, target_mtime_precision)
            result = ftputil.file_transfer.source_is_newer_than_target(
                source_file, target_file
            )
            assert result == expected_result


class FailingStringIO(io.BytesIO):
    """
    Mock class to test whether exceptions are passed on.
    """

    # Kind of nonsense; we just want to see this exception raised.
    expected_exception = IndexError

    def read(self, count):
        raise self.expected_exception


class TestChunkwiseTransfer:
    def _random_string(self, count):
        """
        Return a `BytesIO` object containing `count` "random" bytes.
        """
        ints = (random.randint(0, 255) for i in range(count))
        return bytes(ints)

    def test_chunkwise_transfer_without_remainder(self):
        """
        Check if we get four chunks with 256 Bytes each.
        """
        data = self._random_string(1024)
        fobj = io.BytesIO(data)
        chunks = list(ftputil.file_transfer.chunks(fobj, 256))
        assert len(chunks) == 4
        assert chunks[0] == data[:256]
        assert chunks[1] == data[256:512]
        assert chunks[2] == data[512:768]
        assert chunks[3] == data[768:1024]

    def test_chunkwise_transfer_with_remainder(self):
        """
        Check if we get three chunks with 256 Bytes and one with 253.
        """
        data = self._random_string(1021)
        fobj = io.BytesIO(data)
        chunks = list(ftputil.file_transfer.chunks(fobj, 256))
        assert len(chunks) == 4
        assert chunks[0] == data[:256]
        assert chunks[1] == data[256:512]
        assert chunks[2] == data[512:768]
        assert chunks[3] == data[768:1021]

    def test_chunkwise_transfer_with_exception(self):
        """
        Check if we see the exception raised during reading.
        """
        data = self._random_string(1024)
        fobj = FailingStringIO(data)
        iterator = ftputil.file_transfer.chunks(fobj, 256)
        with pytest.raises(FailingStringIO.expected_exception):
            next(iterator)
