# Copyright (C) 2026, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Tests for deprecation warnings in ftputil 5.2.0.
"""

import datetime
import io
import stat
import subprocess
import sys
import warnings
from unittest import mock

import pytest

with warnings.catch_warnings(category=DeprecationWarning):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import ftputil
    import ftputil.path
    import ftputil.stat

from test import scripted_session
from test import test_base


Call = scripted_session.Call


class TestDeprecationForFilePathEncoding:
    """
    Test the deprecation warning for default path encoding change in
    ftputil 6.0.0.
    """

    def test_import_emits_encoding_warning(self):
        """
        If `ftputil` is imported, it should emit a deprecation warning for the
        upcoming directory/file path encoding change.
        """
        # Run Python in subprocess to test import-time warning.
        result = subprocess.run(
            [
                sys.executable,
                "-W",
                "default::DeprecationWarning",
                "-c",
                "import ftputil",
            ],
            capture_output=True,
            text=True,
        )
        # Check that the warning was emitted.
        assert result.returncode == 0, f"Subprocess failed: {result.stderr}"
        assert "DeprecationWarning" in result.stderr
        assert "ftputil 6.0.0" in result.stderr
        assert "Latin-1" in result.stderr
        assert "UTF-8" in result.stderr
        assert 'encoding="latin-1"' in result.stderr

    def test_warning_points_to_import_location(self, tmp_path):
        """
        The stacklevel of the deprecation warning should point to the user
        code, not to a file in ftputil.
        """
        file_path = tmp_path / "test.py"
        file_path.write_text("import ftputil")
        result = subprocess.run(
            [sys.executable, "-W", "default::DeprecationWarning", file_path],
            capture_output=True,
            text=True,
        )
        # Expect the name of our test file, not of a file in the ftputil package.
        assert "test.py:1: DeprecationWarning:" in result.stderr
        # Don't test for just "ftputil" since it's part of the deprecation message.
        assert "ftputil/" not in result.stderr

    def test_warning_emitted_only_once_per_process(self):
        """
        The deprecation warning should be emitted only once.
        """
        result = subprocess.run(
            [
                sys.executable,
                "-W",
                "defaul::DeprecationWarning",
                "-c",
                "import ftputil\nimport ftputil",
            ],
            capture_output=True,
            text=True,
        )
        warning_count = result.stderr.count("DeprecationWarning")
        assert warning_count == 1, (
            f"Expected exactly one warning, got {warning_count}. stderr: {result.stderr}"
        )


class TestDeprecationForPathWalk:
    """
    Test the deprecation warning for `FTPHost.path.walk` in ftputil 5.2.0.
    """

    def test_path_walk_emits_deprecation_warning(self):
        """
        If `FTPHost.path.walk` is called, it should emit a deprecation warning
        with useful information.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)
        # Don't shadow `warnings` module name.
        with pytest.warns(DeprecationWarning, match="FTPHost.path.walk()") as warnings_:
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)
        assert len(warnings_) >= 1
        walk_warnings = [
            w for w in warnings_ if ("FTPHost.path.walk()" in str(w.message))
        ]
        assert len(walk_warnings) == 1
        # Check deprecation message.
        warning_message = str(walk_warnings[0].message)
        assert "ftputil 6.0.0" in warning_message
        assert "FTPHost.walk()" in warning_message
        assert "deprecated" in warning_message
        assert "os.walk()" in warning_message

    def test_path_walk_warning_can_be_suppressed(self):
        """
        It should be possible to suppress the deprecation warning with a
        warning filter.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)
        # Don't shadow `warnings` module name.
        with warnings.catch_warnings(record=True) as warnings_:
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)
            deprecation_warnings = [
                warning
                for warning in warnings_
                if issubclass(warning.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) == 0

    def test_path_walk_warning_once_per_location(self):
        """
        If the same code calls `FTPHost.path.walk`, only one warning should be
        emitted.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)

        def call_walk():
            # The warning should come from here - once.
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)

        # Don't shadow `warnings` module name.
        with warnings.catch_warnings(record=True) as warnings_:
            warnings.simplefilter("default")
            call_walk()
            call_walk()
            walk_warnings = [
                warning
                for warning in warnings_
                if issubclass(warning.category, DeprecationWarning)
                and "FTPHost.path.walk()" in str(warning.message)
            ]
            assert len(walk_warnings) == 1

    def test_path_walk_warning_from_different_locations(self):
        """
        Verify warning fires separately for different call locations.

        When called from different lines/locations in user code, each
        location should get its own warning.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)

        def call_walk_first():
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)

        def call_walk_second():
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)

        # Don't shadow `warnings` module name.
        with warnings.catch_warnings(record=True) as warnings_:
            warnings.simplefilter("always")
            call_walk_first()
            call_walk_second()
            walk_warnings = [
                warning
                for warning in warnings_
                if issubclass(warning.category, DeprecationWarning)
                and "FTPHost.path.walk()" in str(warning.message)
            ]
            assert len(walk_warnings) == 2

    def test_path_walk_no_warning_on_recursive_calls(self):
        """
        If `FTPHost.path.walk` is called recursively, the inner calls shouldn't
        generate warnings.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.side_effect = lambda path: ["subdir"] if path == "/" else []
        # fmt: off
        dir_stat_result = ftputil.stat.StatResult(
            [
                stat.S_IFDIR | stat.S_IRUSR | stat.S_IXUSR, None, None, None, None,
                None, None, None, None, None,
            ]
        )
        # fmt: on
        mock_host.lstat.return_value = dir_stat_result
        path_obj = ftputil.path._Path(mock_host)

        def visitor(arg, top, names):
            pass

        # Don't shadow `warnings` module name.
        with warnings.catch_warnings(record=True) as warnings_:
            warnings.simplefilter("always")
            path_obj.walk("/", func=visitor, arg=None)
            walk_warnings = [
                warning
                for warning in warnings_
                if issubclass(warning.category, DeprecationWarning)
                and "FTPHost.path.walk()" in str(warning.message)
            ]
            assert len(walk_warnings) == 1
            walk_warning = walk_warnings[0]
            assert "test_deprecations.py" in walk_warning.filename

    def test_path_walk_stacklevel(self):
        """
        If a warning is emitted, it should point to the calling user code, not
        ftputil source files.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)
        # Don't shadow `warnings` module name.
        with warnings.catch_warnings(record=True) as warnings_:
            warnings.simplefilter("always")
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)
            walk_warnings = [
                warning
                for warning in warnings_
                if issubclass(warning.category, DeprecationWarning)
                and "FTPHost.path.walk()" in str(warning.message)
            ]
            assert len(walk_warnings) > 0
            walk_warning = walk_warnings[0]
            assert "test_deprecations.py" in walk_warning.filename
            assert "ftputil/path.py" not in walk_warning.filename


class TestDeprecationForTimeShift:
    """
    Test the deprecation warning for time shift in ftputil 5.2.0.
    """

    @staticmethod
    def _stat_script(name="file"):
        """
        Return a session script for testing `stat`/`lstat`/`getmtime`
        operations.
        """
        dir_line = test_base.dir_line(
            mode_string="-rw-r--r--",
            date_=datetime.date.today(),
            name=name,
        )
        return [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_line),
            Call("cwd", args=("/",)),
            Call("close"),
        ]

    @staticmethod
    def _time_shift_warnings(warnings_):
        """
        Return time shift-related warnings from `warnings_`.
        """
        return [
            warning
            for warning in warnings_
            if issubclass(warning.category, DeprecationWarning)
            and "time shift" in str(warning.message)
        ]

    def _test_stat_like_call_emits_time_shift_warning(self, host_method_name):
        """
        Call the host method `host_method_name` and check that it raised a
        single deprecation warning on setting the time shift explicitly.
        """
        script = self._stat_script("file")
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                host_method = {
                    "stat": host.stat,
                    "lstat": host.lstat,
                    "path.getmtime": host.path.getmtime,
                }
                host_method[host_method_name]("/file")
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 1
                warning = time_shift_warnings[0]
                assert "test_deprecations.py" in warning.filename
                assert "ftputil/host.py" not in warning.filename

    def test_stat_emits_time_shift_warning(self):
        """
        If `FTPHost.stat` is called and the time shift is unset, it should
        emit a deprecation warning with the time shift message.
        """
        self._test_stat_like_call_emits_time_shift_warning("stat")

    def test_lstat_emits_time_shift_warning(self):
        """
        If `FTPHost.lstat` is called and the time shift is unset, it should
        emit a deprecation warning with the time shift message.
        """
        self._test_stat_like_call_emits_time_shift_warning("lstat")

    def test_getmtime_emits_time_shift_warning(self):
        """
        If `FTPHost.path.getmtime` is called and the time shift is unset,
        it should emit a deprecation warning with the time shift message.
        """
        self._test_stat_like_call_emits_time_shift_warning("path.getmtime")

    def test_listdir_does_not_emit_time_shift_warning(self):
        """
        `FTPHost.listdir` should _not_ emit a time shift deprecation warning
        because it doesn't return timestamps.
        """
        script = self._stat_script("file")
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                _items = host.listdir("/")
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 0

    def test_listdir_and_stat_emits_time_shift_warning(self):
        """
        If `listdir` alone is used, it shouldn't emit a time shift warning, see
        above. But a following `stat` (or other function that actually exposes
        time data) should warn then.
        """
        script = self._stat_script("file")
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                # This implicitly reads and stats the directory entries, the
                # subsequent `stat` call doesn't actually fetch stat data from
                # the host.
                _items = host.listdir("/")
                _stat_result = host.stat("file")
                time_shift_warnings = self._time_shift_warnings(warnings_)
                # We know that the warning comes from the `stat` call because
                # we have the test
                # `test_listdir_does_not_emit_time_shift_warning` above that
                # shows that `listdir` alone doesn't emit a warning.
                assert len(time_shift_warnings) == 1
                warning = time_shift_warnings[0]
                assert "test_deprecations.py" in warning.filename
                assert "ftputil/host.py" not in warning.filename

    def test_upload_if_newer_emits_time_shift_warning(self, tmp_path):
        """
        If `FTPHost.upload_if_newer` is called and the time shift is unset,
        it should emit a deprecation warning with the time shift message.
        """
        local_source = tmp_path / "test_source"
        local_source.write_bytes(b"test content")
        # Target is newer, so no upload happens.
        dir_result = test_base.dir_line(
            mode_string="-rw-r--r--",
            date_=datetime.date.today() + datetime.timedelta(days=1),
            name="newer",
        )
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_result),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                host.upload_if_newer(str(local_source), "/newer")
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 1
                warning = time_shift_warnings[0]
                assert "test_deprecations.py" in warning.filename
                assert "ftputil/host.py" not in warning.filename

    def test_download_if_newer_emits_time_shift_warning(self, tmp_path):
        """
        If `FTPHost.download_if_newer` is called and the time shift is unset,
        it should emit a deprecation warning with the time shift message.
        """
        local_target = tmp_path / "test_target"
        local_target.touch()
        # Target is older, so download happens.
        dir_result = test_base.dir_line(
            mode_string="-rw-r--r--",
            date_=datetime.date.today() + datetime.timedelta(days=1),
            name="newer",
        )
        host_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_result),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call("transfercmd", args=("RETR newer", None), result=io.BytesIO(b"data")),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                host.download_if_newer("/newer", str(local_target))
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 1
                warning = time_shift_warnings[0]
                assert "test_deprecations.py" in warning.filename
                assert "ftputil/host.py" not in warning.filename

    def test_time_shift_emits_warning_when_unset(self):
        """
        If `FTPHost.time_shift()` is called directly and the time shift is
        unset, it should emit a deprecation warning.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                host.time_shift()
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 1
                warning = time_shift_warnings[0]
                assert "test_deprecations.py" in warning.filename
                assert "ftputil/host.py" not in warning.filename

    def test_set_time_shift_does_not_emit_warning(self):
        """
        `FTPHost.set_time_shift` should _not_ emit a time shift deprecation
        warning because it's the method to set the time shift.
        """
        script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("close"),
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                host.set_time_shift(3600)
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 0

    def test_set_time_shift_zero_suppresses_subsequent_warning(self):
        """
        Calling `set_time_shift(0.0)` on an `FTPHost` without a prior
        `set_time_shift` call should behave the same as setting any other
        value: subsequent stat-like operations must not emit the deprecation
        warning.

        This test was added because of a bug in a former implementation that
        emitted the warning again after a previous call of
        `host.set_time_shift(0.0)`.
        """
        script = self._stat_script("file")
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            host.set_time_shift(0.0)
            # Explicit setting must flip `_time_shift` away from the sentinel.
            assert host._time_shift == 0.0
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                host.stat("/file")
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 0

    def test_synchronize_times_does_not_emit_warning(self):
        """
        `FTPHost.synchronize_times` should _not_ emit a time shift deprecation
        warning even though it internally calls `getmtime` (which would
        normally warn on an unset time shift).

        `synchronize_times` behaves like `set_time_shift` in the sense that it
        _sets_ a time shift.
        """
        # Freeze both client and server clocks at the same instant so the
        # measured time shift is 0.0 and set_time_shift(0.0) is valid.
        frozen = "2026-04-19 12:00:00"
        dir_listing = test_base.dir_line(
            mode_string="-rw-r--r--",
            datetime_=datetime.datetime(2026, 4, 19, 12, 0),
            name="_ftputil_sync_",
        )
        host_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            # `getmtime` -> `stat` -> `_dir` traversal
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("dir", args=("",), result=dir_listing),
            Call("cwd", args=("/",)),
            # `unlink` -> `_robust_ftp_command` traversal
            Call("cwd", args=("/",)),
            Call("cwd", args=("/",)),
            Call("delete", args=("_ftputil_sync_",)),
            Call("cwd", args=("/",)),
            Call("close"),
        ]
        file_script = [
            Call("__init__"),
            Call("pwd", result="/"),
            Call("cwd", args=("/",)),
            Call("voidcmd", args=("TYPE I",)),
            Call(
                "transfercmd",
                args=("STOR _ftputil_sync_", None),
                result=io.BytesIO(),
            ),
            Call("voidresp"),
            Call("close"),
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with freezegun.freeze_time(frozen):
            with test_base.ftp_host_factory(multisession_factory) as host:
                with warnings.catch_warnings(record=True) as warnings_:
                    warnings.simplefilter("default")
                    host.synchronize_times()
                    time_shift_warnings = self._time_shift_warnings(warnings_)
                    assert len(time_shift_warnings) == 0

    def test_warning_emitted_only_once_per_host(self):
        """
        The time shift warning should be emitted only once per host instance,
        even if multiple methods that need the time shift are called.
        """
        script = self._stat_script("file")
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                host.stat("/file")
                host.lstat("/file")
                host.time_shift()
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 1

    def test_different_hosts_each_warn_once_for_different_client_calls(self):
        """
        Each host instance should emit its own warning, since the sentinel
        is per-instance. The `"always"` filter is used (rather than the
        `"default"` used elsewhere in this class) so that Python's
        per-location deduplication doesn't mask the per-host emissions we want
        to verify.
        """
        script = self._stat_script("file")
        with (
            test_base.ftp_host_factory(scripted_session.factory(script)) as host1,
            test_base.ftp_host_factory(scripted_session.factory(script)) as host2,
        ):
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("always")
                host1.stat("/file")
                host2.stat("/file")
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 2

    # This is extracted as its own method, so that it counts as the same
    # location in the source code calling into the same ftputil method.
    @staticmethod
    def _call_host_stat(host):
        host.stat("/file")

    def test_warning_emitted_only_once_per_same_client_call_for_different_hosts(self):
        """
        The time shift warning should be emitted only once per location in
        client code, even when the two calls operate on different `FTPHost`
        instances. Relies on Python's default deduplication for
        `DeprecationWarning` by `(message, category, module, lineno)`.
        """
        script = self._stat_script("file")
        with (
            test_base.ftp_host_factory(scripted_session.factory(script)) as host1,
            test_base.ftp_host_factory(scripted_session.factory(script)) as host2,
        ):
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                self._call_host_stat(host1)
                self._call_host_stat(host2)
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 1

    def test_time_shift_value_is_zero_after_warning(self):
        """
        After the first warning, the time shift should be set to 0.0 (the
        pre-5.2 default).
        """
        script = self._stat_script("file")
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            with warnings.catch_warnings(record=True) as warnings_:
                warnings.simplefilter("default")
                host.stat("/file")
                assert host.time_shift() == 0.0
                time_shift_warnings = self._time_shift_warnings(warnings_)
                assert len(time_shift_warnings) == 1
