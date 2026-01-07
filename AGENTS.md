# ftputil Development Guide for Coding Agents

## Introduction

ftputil is a high-level FTP client library "above" `ftplib.FTP`. The
methods of `ftputil.FTPHost` objects mimic functions/methods in the
`os`, `os.path` and `shutil` modules and there are convenience methods
like `upload` and `upload_if_newer`. It's also possible to create
remote file-like objects.

## Build/test commands

- **Run fast tests**: `make test` or `python -m pytest -m "not slow_test" test`
- **Run all tests**: `make all_tests` or `python -m pytest test`
- **Run single test**: `python -m pytest test/test_<module>.py::<TestClass>::<test_method>`
- **Run with coverage**: `py.test --cov ftputil --cov-report html test`
- **Lint code**: `make pylint` or `pylint --rcfile=pylintrc ftputil/*.py`
- **Build distribution**: `make dist`
- **Run tox (multi-version testing)**: `tox`

## Code style guidelines

- **Max line length**: 88 characters (follows pylintrc config)
- **Empty lines in functions/methods:** Avoid empty lines, except around
  function/method-internal `def` or `class` statements
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Standard library first, then ftputil modules (see host.py example)
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error handling**: Use context managers like `ftplib_error_to_ftp_os_error`
- **Docstrings**: Module-level docstrings required, function docstrings encouraged
- **Type hints**: Not extensively used in this codebase
- **Comments**: Standard copyright header with Stefan Schwarzer attribution

## Testing

- Uses pytest framework with custom markers (`slow_test` for long-running tests)
- Test files follow `test_<module>.py` naming pattern in `test/` directory
- Test docstrings should use style from behavior-driven testing, but without
  explicit Given/When distinction. See `test_host.py` for examples.
- Use `scripted_session` for FTP session mocking
- Dependencies: pytest, freezegun (see tox.ini)

### Mocking approach

Most tests use a "scripted session" mocking approach. A "session" in
this context is an object whose API is compatible with the API of
`ftplib.FTP`. Every instance of the `FTPHost` class has an attribute
`_session`, which is an instance of the session class to use.

In normal use of ftputil, a session is an instance of `ftplib.FTP` or
`ftplib.FTPS`, but the concrete class/factory can be overridden with
the `session_factory` argument of the `FTPHost` constructor. This is
also used for dependency injection for tests, where the session
factory returns an instance of `test.scripted_session.ScriptedSession`
or `test.scripted_session.MultisessionFactory`.

The behavior of a `ScriptedSession` is determined by passing it a
`script` object, which is a list of `Call` objects. Each such object
defines the name of a `ftplib.FTP` method to call, the arguments of
the call and the result that should be returned by the mock object.

For example, `test.test_host.TestConstructor.test_open_and_close` is
```python
    def test_open_and_close(self):
        """
        Test if opening and closing an `FTPHost` object works as expected.
        """
        script = [Call("__init__"), Call("pwd", result="/"), Call("close")]
        host = test_base.ftp_host_factory(scripted_session.factory(script))
        host.close()
        assert host.closed is True
        assert host._children == []
```

At test runtime, the mock object will ensure that the
`ScriptedSession` is called with the method defined in the `Call`
object, and the mock call will return (or raise) the `Call.result`
defined in the test setup.

`MultisessionFactory` is an extension of `ScriptedSession` that uses
different `ScriptedSession`s for consecutive `FTPHost` constructions,
similar to the use of the `side_effect` in `unittest.mock` that can be
used to define consecutive return values for multiple calls. Defining
multiple sessions is important for testing FTP file-like objects,
which are `FTPFile` instances that contain `FTPHost` instances as
their `_file` attribute.

An advantage of the "scripted session" approach is that it's extremely
flexible, but the downside is that the "script" also has to define
"lower" call levels that aren't really part of what the actual test
should test. In other words, the scripted session may need to be
adapted if the _implementation_ of the function/method under test
changes.
