# Copyright (C) 2026, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Tests for deprecation warnings in ftputil 5.2.0.
"""

import datetime
import subprocess
import sys
import warnings
from unittest import mock

import pytest

# Ignore warning from following `ftputil` import.
warnings.filterwarnings("ignore", category=DeprecationWarning)

import ftputil
import ftputil.path

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
        Verify that importing ftputil emits the path encoding
        deprecation warning.
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
        Verify that stacklevel is set correctly to point to user code.
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
        Verify that the warning is emitted only once, even with multiple imports.
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
        Verify that calling `path.walk` emits a deprecation warning.

        Tests that the warning is emitted when path.walk() is called.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)
        with pytest.warns(DeprecationWarning, match="FTPHost.path.walk()"):
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)

    def test_path_walk_warning_message_content(self):
        """
        Verify warning message provides clear guidance.

        The warning should mention ftputil 6.0.0, FTPHost.walk(), and reference
        to os.walk() to help users understand the alternative.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)
        with pytest.warns(DeprecationWarning) as record:
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)
        assert len(record) >= 1
        walk_warnings = [w for w in record if "FTPHost.path.walk()" in str(w.message)]
        assert len(walk_warnings) >= 1
        warning_message = str(walk_warnings[0].message)
        assert "ftputil 6.0.0" in warning_message
        assert "FTPHost.walk()" in warning_message
        assert "deprecated" in warning_message
        assert "os.walk()" in warning_message

    def test_path_walk_no_warning_on_recursive_call(self):
        """
        Verify that no warning is emitted on internal recursive calls.

        When path.walk() calls itself recursively via _is_recursive_call=True,
        no deprecation warning should be emitted.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)
        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            path_obj.walk(
                "/",
                func=lambda arg, top, names: None,
                arg=None,
                _is_recursive_call=True,
            )
        walk_warnings = [w for w in record if "FTPHost.path.walk()" in str(w.message)]
        assert len(walk_warnings) == 0

    def test_path_walk_warning_can_be_suppressed(self):
        """
        Verify warning can be suppressed with warnings filters.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)
            deprecation_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) == 0

    def test_path_walk_warning_once_per_location(self):
        """
        Verify warning uses Python's default filter (once per location).

        The default warning filter suppresses duplicate warnings from the
        same source location. This test verifies the warning is emitted with
        the default filter active, and can be seen from different locations.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("default")
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)
            walk_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
                and "FTPHost.path.walk()" in str(warning.message)
            ]
            assert len(walk_warnings) >= 1

    def test_path_walk_warning_different_locations(self):
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

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            call_walk_first()
            call_walk_second()
            walk_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
                and "FTPHost.path.walk()" in str(warning.message)
            ]
            assert len(walk_warnings) == 2

    def test_path_walk_stacklevel(self):
        """
        Verify stacklevel=2 points to caller's code, not ftputil internals.
        """
        mock_host = mock.MagicMock()
        mock_host._encoding = "utf-8"
        mock_host.listdir.return_value = []
        path_obj = ftputil.path._Path(mock_host)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            path_obj.walk("/", func=lambda arg, top, names: None, arg=None)
            walk_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
                and "FTPHost.path.walk()" in str(warning.message)
            ]
            assert len(walk_warnings) > 0
            warning = walk_warnings[0]
            assert "test_deprecations.py" in warning.filename
            assert "ftputil/path.py" not in warning.filename
