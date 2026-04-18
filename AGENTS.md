# ftputil Development Guide for Coding Agents

## Introduction

ftputil is a high-level FTP client library "above" `ftplib.FTP`. The
methods of `ftputil.FTPHost` objects mimic functions/methods in the
`os`, `os.path` and `shutil` modules and there are convenience methods
like `upload` and `upload_if_newer`. It's also possible to create
remote file-like objects.

## Build/test commands

- **Run fast tests**: `make test` or `python -m pytest -m "not slow" test`
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

- Uses pytest framework with custom markers (`slow` for long-running tests)
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

#### Basic `ScriptedSession` usage

The behavior of a `ScriptedSession` is determined by passing it a
`script` object, which is a list of `Call` objects. Each such object
defines:
- `method_name`: the name of the `ftplib.FTP` method to call
- `args`: positional arguments expected (as a tuple), or `None` to skip validation
- `kwargs`: keyword arguments expected (as a dict), or `None` to skip validation
- `result`: the value to return, or an exception to raise

For example, `test.test_host.TestConstructor.test_open_and_close` is:
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

#### Common patterns

**Basic FTP host test pattern:**

```python
script = [
    Call("__init__"),
    Call("pwd", result="/"),
    # ... your operation calls here ...
    Call("close")
]
host = test_base.ftp_host_factory(scripted_session.factory(script))
# ... test code ...
host.close()
```

**Testing error conditions:**

Pass an exception as the `result`:
```python
Call("cwd", args=("/nonexistent",), result=ftplib.error_perm)
```

**Directory listings:**

Use `test_base.dir_line()` helper to generate realistic `DIR` output:
```python
import datetime
listing = "\n".join([
    test_base.dir_line(
        mode_string="drwxr-xr-x",
        name="somedir",
        datetime_=datetime.datetime(2019, 4, 22, 16, 50)
    ),
    test_base.dir_line(
        mode_string="-rw-r--r--",
        name="somefile.txt",
        size=1024,
        datetime_=datetime.datetime(2019, 4, 22, 16, 51)
    )
])
script = [
    Call("__init__"),
    Call("pwd", result="/"),
    Call("dir", args=("/somepath",), result=listing),
    Call("close")
]
```

**File operations:**

Use `io.BytesIO` or `io.StringIO` for file content:
```python
Call("transfercmd",
     args=("RETR somefile.txt", None),
     result=io.BytesIO(b"file contents"))
```

#### `MultisessionFactory`

`MultisessionFactory` is used when a test needs multiple FTP sessions,
such as when testing file operations. `FTPFile` instances create their
own `FTPHost` internally, which requires a second session.

The factory is called with multiple scripts, one for each session:
```python
host_script = [
    Call("__init__"),
    Call("pwd", result="/"),
    Call("close")
]
file_script = [
    Call("__init__"),
    Call("pwd", result="/"),
    Call("cwd", args=("/",)),
    Call("voidcmd", args=("TYPE I",)),
    Call("transfercmd", args=("STOR myfile.txt", None), result=io.BytesIO()),
    Call("voidresp"),
    Call("close"),
]
multisession_factory = scripted_session.factory(host_script, file_script)
with test_base.ftp_host_factory(multisession_factory) as host:
    with host.open("myfile.txt", "w") as f:
        f.write("data")
```

The first call to create a session uses `host_script`, the second uses
`file_script`, and so on for additional scripts.

#### Helper utilities

- `test_base.ftp_host_factory(session_factory)`: Creates an `FTPHost`
  with dummy credentials and the given session factory
- `test_base.dir_line(...)`: Generates realistic FTP `DIR` command
  output lines with configurable attributes (mode, size, timestamps, etc.)
- `test_base.MockableBytesIO` and `test_base.MockableStringIO`:
  Subclasses of `io.BytesIO`/`io.StringIO` that can be mocked with
  `unittest.mock` (needed because built-in classes can't be patched)

#### Special method handling

Some `ftplib.FTP` methods have special implementations in `ScriptedSession`:
- `dir(path, callback)`: Splits the `result` string by lines and calls
  the callback for each line
- `transfercmd(cmd, rest)`: Returns a mock socket whose `makefile()`
  returns the `result` value
- `ntransfercmd(cmd, rest)`: Returns a tuple of (mock socket, size)

#### Writing new tests: workflow

1. Identify the ftputil operation you want to test (e.g., `host.listdir()`)
2. Trace through the code to determine which `ftplib.FTP` methods will be called
3. Create a script with `Call` objects for each expected method call:
   - Always start with `Call("__init__")`
   - Usually need `Call("pwd", result="/")`  early on
   - Add calls for your specific operation
   - End with `Call("close")` if you close the host
4. For file operations, create separate scripts for host and file sessions
5. Use `test_base.ftp_host_factory()` to create the host with your scripted session

#### Trade-offs

**Advantages:**

- Extremely flexible and powerful
- Makes the sequence of FTP commands explicit and testable
- No network I/O needed

**Disadvantages:**

- Scripts can become verbose with "plumbing" calls not directly related
  to the test's purpose
- Scripts are tied to implementation details and may need updates when
  the internal call sequence changes
- Requires understanding both the ftputil code and the underlying
  `ftplib.FTP` API

**Tip:** When a test fails with "Ran out of `Call` objects", it means
the code under test made more FTP calls than expected. When a test
fails with a method name mismatch, the code called a different FTP
method than expected. In both cases, review the test output to see
what was expected vs. what actually happened, then update your script
accordingly.
