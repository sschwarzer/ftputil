# Copyright (C) 2008-2019, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import ftplib
import io
import pytest

import ftputil.error

import test.scripted_session as scripted_session
from test import test_base
from test.test_file import InaccessibleDirSession, ReadMockSession


Call = scripted_session.Call


# Exception raised by client code, i. e. code using ftputil. Used to
# test the behavior in case of client exceptions.
class ClientCodeException(Exception):
    pass


#
# Test cases
#
class TestHostContextManager:

    def test_normal_operation(self):
        script = [
          Call(method_name="__init__"),
          Call(method_name="pwd", result="/"),
          Call(method_name="close")
        ]
        with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
            assert host.closed is False
        assert host.closed is True

    def test_ftputil_exception(self):
        script = [
          # Since `__init__` raises an exception, `pwd` isn't called. However,
          # `close` is called via the context manager.
          Call(method_name="__init__", result=ftplib.error_perm),
          Call(method_name="close")
        ]
        with pytest.raises(ftputil.error.FTPOSError):
            with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
                pass
        # We arrived here, that's fine. Because the `FTPHost` object
        # wasn't successfully constructed, the assignment to `host`
        # shouldn't have happened.
        assert "host" not in locals()

    def test_client_code_exception(self):
        script = [
          Call(method_name="__init__"),
          Call(method_name="pwd", result="/"),
          Call(method_name="close")
        ]
        try:
            with test_base.ftp_host_factory(scripted_session.factory(script)) as host:
                assert host.closed is False
                raise ClientCodeException()
        except ClientCodeException:
            assert host.closed is True
        else:
            pytest.fail("`ClientCodeException` not raised")


class TestFileContextManager:

    def test_normal_operation(self):
        host_script = [
          Call(method_name="__init__"),
          Call(method_name="pwd", result="/"),
          Call(method_name="close")
        ]
        file_script = [
          Call(method_name="__init__"),
          Call(method_name="pwd", result="/"),
          Call(method_name="cwd", result=None, args=("/",)),
          Call(method_name="voidcmd", result=None, args=("TYPE I",)),
          Call(method_name="transfercmd",
               result=io.BytesIO(b"line 1\nline 2"),
               args=("RETR dummy", None)),
          Call(method_name="voidresp", result=None),
          Call(method_name="close")
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with host.open("dummy", "r") as fobj:
                assert fobj.closed is False
                data = fobj.readline()
                assert data == "line 1\n"
                assert fobj.closed is False
            assert fobj.closed is True

    def test_ftputil_exception(self):
        host_script = [
          Call(method_name="__init__"),
          Call(method_name="pwd", result="/"),
          Call(method_name="close")
        ]
        file_script = [
          Call(method_name="__init__"),
          Call(method_name="pwd", result="/"),
          Call(method_name="cwd", result=None, args=("/",)),
          Call(method_name="voidcmd", result=None, args=("TYPE I",)),
          # Raise exception. `voidresp` therefore won't be called, but `close`
          # will be called by the context manager.
          Call(method_name="transfercmd",
               result=ftplib.error_perm,
               args=("STOR inaccessible", None)),
          # Call(method_name="voidresp", result=None),
          Call(method_name="close")
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            with pytest.raises(ftputil.error.FTPIOError):
                # This should fail.
                with host.open("/inaccessible", "w") as fobj:
                    pass
            # The file construction shouldn't have succeeded, so `fobj`
            # should be absent from the local namespace.
            assert "fobj" not in locals()

    def test_client_code_exception(self):
        host_script = [
          Call(method_name="__init__"),
          Call(method_name="pwd", result="/"),
          Call(method_name="close")
        ]
        file_script = [
          Call(method_name="__init__"),
          Call(method_name="pwd", result="/"),
          Call(method_name="cwd", result=None, args=("/",)),
          Call(method_name="voidcmd", result=None, args=("TYPE I",)),
          Call(method_name="transfercmd",
               result=io.BytesIO(b""),
               args=("RETR dummy", None)),
          Call(method_name="voidresp", result=None),
          Call(method_name="close")
        ]
        multisession_factory = scripted_session.factory(host_script, file_script)
        with test_base.ftp_host_factory(multisession_factory) as host:
            try:
                with host.open("dummy", "r") as fobj:
                    assert fobj.closed is False
                    raise ClientCodeException()
            except ClientCodeException:
                assert fobj.closed is True
            else:
                pytest.fail("`ClientCodeException` not raised")
