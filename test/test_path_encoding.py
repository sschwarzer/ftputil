# Copyright (C) 2026, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

"""
Tests for file path encoding deprecation warnings in ftputil 5.2.0
"""

import subprocess
import sys
import textwrap

import pytest


class TestEncodingDeprecationWarning:
    """
    Test the deprecation warning for default encoding change in ftputil 6.0.0
    """

    def test_import_emits_encoding_warning(self):
        """
        Verify that importing ftputil emits the encoding deprecation warning.
        """
        # Run Python in subprocess to test import-time warning
        code = textwrap.dedent("""
            import warnings
            warnings.simplefilter('default', DeprecationWarning)
            import ftputil
        """)
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True
        )
        # Check that warning was emitted
        assert result.returncode == 0, f"Subprocess failed: {result.stderr}"
        assert "DeprecationWarning" in result.stderr
        assert "ftputil 6.0.0" in result.stderr
        assert "Latin-1" in result.stderr
        assert "UTF-8" in result.stderr
        assert 'encoding="latin-1"' in result.stderr

    def test_warning_emitted_only_once_per_process(self):
        """
        Verify that the warning is emitted only once, even with multiple imports.
        """
        code = textwrap.dedent("""
            import warnings
            warnings.simplefilter('default', DeprecationWarning)
            import ftputil
            # Import again (should not emit warning again due to module cache)
            import ftputil
        """)
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True
        )
        # Count occurrences of the warning
        warning_count = result.stderr.count("DeprecationWarning")
        assert warning_count == 1, (
            f"Expected exactly 1 warning, got {warning_count}. stderr: {result.stderr}"
        )

    def test_warning_can_be_suppressed(self):
        """
        Verify that the warning can be suppressed with warnings.filterwarnings.
        """
        code = textwrap.dedent("""
            import warnings
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            import ftputil
        """)
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True
        )
        # Check that no warning was emitted
        assert result.returncode == 0
        assert "DeprecationWarning" not in result.stderr

    def test_warning_message_actionable(self):
        """
        Verify the warning message provides clear action items.
        """
        code = textwrap.dedent("""
            import warnings
            warnings.simplefilter('default', DeprecationWarning)
            import ftputil
        """)
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True
        )
        stderr = result.stderr
        # Check for actionable guidance
        assert "encoding=" in stderr or "explicitly specify" in stderr

    def test_warning_points_to_import_location(self):
        """
        Verify that stacklevel is set correctly to point to user code.
        """
        code = textwrap.dedent("""
            import warnings
            warnings.simplefilter('always', DeprecationWarning)
            import ftputil
        """)
        result = subprocess.run(
            [sys.executable, "-W", "default::DeprecationWarning", "-c", code],
            capture_output=True,
            text=True,
        )
        # The warning should reference the import line, not ftputil
        # internals. We can't check exact line numbers in `-c` mode,
        # but we can verify it doesn't point to ftputil/__init__.py in
        # the first line of `stderr`.
        first_line = result.stderr.split("\n")[0] if result.stderr else ""
        assert "ftputil/__init__.py" not in first_line, (
            "Warning should point to user code, not ftputil internals"
        )
