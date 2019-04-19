# Copyright (C) 2018-2019, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import unittest.mock


__all__ = ["Call", "factory"]


class Call:

    def __init__(self, method_name, result=None,
                 expected_args=None, expected_kwargs=None):
        self.method_name = method_name
        self.result = result
        self.expected_args = expected_args
        self.expected_kwargs = expected_kwargs

    def __repr__(self):
        return ("{0.__class__.__name__}("
                "method_name={0.method_name!r}, "
                "result={0.result!r}, "
                "expected_args={0.expected_args!r}, "
                "expected_kwargs={0.expected_kwargs!r})".format(self))

    def check_args(self, args, kwargs):
        """
        Check if `args` and `kwargs` that were used in the actual call match
        what was expected.
        """
        if self.expected_args is not None:
            assert args == self.expected_args
        if self.expected_kwargs is not None:
            assert kwargs == self.expected_kwargs

    @staticmethod
    def _is_exception_class(obj):
        """
        Return `True` if `obj` is an exception class, else `False`.
        """
        try:
            return issubclass(obj, Exception)
        except TypeError:
            # TypeError: issubclass() arg 1 must be a class
            return False

    def __call__(self):
        """
        Simulate call, returning the result or raising the exception.
        """
        if isinstance(self.result, Exception) or self._is_exception_class(self.result):
            raise self.result
        else:
            return self.result


class ScriptedSession:
    """
    "Scripted" `ftplib.FTP`-like class for testing.

    To avoid actual input/output over sockets or files, specify the
    values that should be returned by the class's methods.

    The class is instantiated with a `script` argument. This is a list
    of `Call` objects where each object specifies the name of the
    `ftplib.FTP` method that is expected to be called and what the
    method should return. If the value is an exception, it will be
    raised, not returned.

    In case the method returns a socket (like `transfercmd`), the
    return value to be specified in the `Call` instance is the content
    of the underlying socket file.

    The advantage of the approach of this class over the use of
    `unittest.mock.Mock` objects is that the sequence of calls is
    clearly visible. With `Mock` objects, the developer must keep in
    mind all the calls when specifying return values or side effects
    for the mock methods.
    """

    # Class-level counter to enumerate `ScriptedSession`s. This makes it
    # possible to make the output even more compact. Additionally, it's easier
    # to distinguish numbers like 1, 2, etc. than hexadecimal ids.
    _session_count = 0

    def __init__(self, script):
        self.script = script
        # Index into `script`, the list of `Call` objects
        self._call_index = 0
        self.__class__._session_count += 1
        self._session_count = self.__class__._session_count
        # Always expect an entry for the constructor.
        init = self._next_call(expected_method_name="__init__")
        # The constructor isn't supposed to return anything. The only
        # reason to call it here is to raise an exception if that was
        # specified in the `script`.
        init()

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self._session_count)

    def _print(self, text):
        """
        Print `text`, prefixed with a `repr` of the `ScriptedSession`
        instance.
        """
        print("{}: {}".format(self, text))

    def _next_call(self, expected_method_name=None):
        """
        Return next `Call` object.

        Print the `Call` object before returning it. This is useful for
        testing and debugging.
        """
        self._print("Expecting method name {!r} ...".format(expected_method_name))
        try:
            call = self.script[self._call_index]
        except IndexError:
            self._print("*** Ran out of `Call` objects for this session")
            raise
        self._call_index += 1
        if expected_method_name is not None:
            assert call.method_name == expected_method_name, (
                     "called method {!r} instead of {!r}".format(expected_method_name,
                                                                 call.method_name))
            self._print("  found method {!r}".format(expected_method_name))
        return call

    def __getattr__(self, attribute_name):
        call = self._next_call(expected_method_name=attribute_name)
        def dummy_method(*args, **kwargs):
            self._print("{!r} is called with:".format(call))
            self._print("  args: {!r}".format(args))
            self._print("  kwargs: {!r}".format(kwargs))
            call.check_args(args, kwargs)
            return call()
        return dummy_method

    # ----------------------------------------------------------------------
    # `ftplib.FTP` methods that shouldn't be executed with the default
    # processing in `__getattr__`

    # `File.close` accesses the session `sock` object to set and reset the
    # timeout. `sock` itself is never _called_ though, so it doesn't make sense
    # to create a `sock` _call_.
    sock = unittest.mock.Mock(name="socket_attribute")

    def dir(self, path, callback):
        """
        Call the `callback` for each line in the multiline string
        `call.result`.
        """
        call = self._next_call(expected_method_name="dir")
        for line in call.result.splitlines():
            callback(line)

    def ntransfercmd(self, cmd, rest=None):
        """
        Simulate the `ftplib.FTP.ntransfercmd` call.

        `ntransfercmd` returns a tuple of a socket and a size argument. The
        `result` value given when constructing an `ntransfercmd` call specifies
        an `io.TextIO` or `io.BytesIO` value to be used as the
        `Socket.makefile` result.
        """
        call = self._next_call(expected_method_name="ntransfercmd")
        mock_socket = unittest.mock.Mock(name="socket")
        mock_socket.makefile.return_value = call.result
        # Return `None` for size. The docstring of `ftplib.FTP.ntransfercmd`
        # says that's a possibility.
        # TODO: Use a sensible `size` value later if it turns out we need it.
        return mock_socket, None

    def transfercmd(self, cmd, rest=None):
        """
        Simulate the `ftplib.FTP.transfercmd` call.

        `transfercmd` returns a socket. The `result` value given when
        constructing an `transfercmd` call specifies an `io.TextIO` or
        `io.BytesIO` value to be used as the `Socket.makefile` result.
        """
        return self.ntransfercmd(cmd, rest)[0]


class MultisessionFactory:
    """
    Return a session factory using the scripted data from the given
    "scripts" for each consecutive call ("creation") of a factory.

    Example:

      host = ftputil.FTPHost(host, user, password,
                             session_factory=scripted_session.factory(script1, script2))

    When the `session_factory` is "instantiated" for the first time by
    `FTPHost._make_session`, the factory object will use the behavior
    described by the script `script1`. When the `session_factory` is
    "instantiated" a second time, the factory object will use the
    behavior described by the script `script2`.
    """

    def __init__(self, *scripts):
        self._scripts = iter(scripts)

    def __call__(self, host, user, password):
        """
        Call the factory.

        This is equivalent to the constructor of the session (e. g.
        `ftplib.FTP` in a real application).
        """
        script = next(self._scripts)
        return ScriptedSession(script)


factory = MultisessionFactory
