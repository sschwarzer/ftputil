# Copyright (C) 2026, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Tests for deprecation warnings in ftputil 5.2.0.
"""

import datetime
import stat
import subprocess
import sys
import warnings
from unittest import mock

import pytest

# Ignore warning from following `ftputil` import.
warnings.filterwarnings("ignore", category=DeprecationWarning)

import ftputil
import ftputil.path
import ftputil.stat

from test import test_base
from test import scripted_session


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
