# Copyright (C) 2018-2019, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import unittest.mock


__all__ = ["Call", "factory"]


class Call:

    def __init__(self, method_name, result=None, args=None, kwargs=None):
        self.method_name = method_name
        self.result = result
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return ("{0.__class__.__name__}("
                "method_name={0.method_name!r}, "
                "result={0.result!r}, "
                "args={0.args!r}, "
                "kwargs={0.kwargs!r})".format(self))

    def check_method_name(self, method_name):
        """
        Check if the `method_name` matches the method name of this scripted
        call.
        """
        # This is a simple implementation, but keep it for consistency with
        # `check_args`.
        if self.method_name is not None:
            assert method_name == self.method_name

    def check_args(self, args, kwargs):
        """
        Check if `args` and `kwargs` that were used in the actual call match
        what was expected.
        """
        if self.args is not None:
            assert args == self.args
        if self.kwargs is not None:
            assert kwargs == self.kwargs

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
        init = self._next_script_call()
        init.check_method_name("__init__")
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

    def _next_script_call(self):
        """
        Return next `Call` object.
        """
        try:
            call = self.script[self._call_index]
        except IndexError:
            self._print("*** Ran out of `Call` objects for this session")
            raise
        self._call_index += 1
        return call

    def _print_method_names(self, script_method_name, sut_method_name):
        """
        Print the name of the method specified in the scripted session and the
        name of the method called from the system under test.
        """
        self._print("Method name from script: {!r}".format(script_method_name))
        self._print("Method name from system under test: {!r}".format(sut_method_name))

    def _print_args(self, script_args, script_kwargs, sut_args, sut_kwargs):
        """
        Print the expected args and kwargs of the scripted session and the
        args and kwargs from the system under test.
        """
        self._print("args from script: {!r}".format(script_args))
        self._print("kwargs from script: {!r}".format(script_kwargs))
        self._print("args from system under test: {!r}".format(sut_args))
        self._print("kwargs from system under test: {!r}".format(sut_kwargs))

    def __getattr__(self, attribute_name):
        script_call = self._next_script_call()
        self._print_method_names(script_call.method_name, attribute_name)
        script_call.check_method_name(attribute_name)
        def dummy_method(*args, **kwargs):
            self._print_args(script_call.args, script_call.kwargs, args, kwargs)
            script_call.check_args(args, kwargs)
            return script_call()
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
        script_call = self._next_script_call()
        self._print_method_names(script_call.method_name, "dir")
        for line in script_call.result.splitlines():
            callback(line)

    def ntransfercmd(self, cmd, rest=None):
        """
        Simulate the `ftplib.FTP.ntransfercmd` call.

        `ntransfercmd` returns a tuple of a socket and a size argument. The
        `result` value given when constructing an `ntransfercmd` call specifies
        an `io.TextIO` or `io.BytesIO` value to be used as the
        `Socket.makefile` result.
        """
        script_call = self._next_script_call()
        self._print_method_names(script_call.method_name, "ntransfercmd")
        script_call.check_method_name("ntransfercmd")
        mock_socket = unittest.mock.Mock(name="socket")
        mock_socket.makefile.return_value = script_call.result
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
        script_call = self._next_script_call()
        self._print_method_names(script_call.method_name, "transfercmd")
        script_call.check_method_name("transfercmd")
        mock_socket = unittest.mock.Mock(name="socket")
        mock_socket.makefile.return_value = script_call.result
        return mock_socket


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
        self.scripted_sessions = []

    def __call__(self, host, user, password):
        """
        Call the factory.

        This is equivalent to the constructor of the session (e. g.
        `ftplib.FTP` in a real application).
        """
        script = next(self._scripts)
        scripted_session = ScriptedSession(script)
        self.scripted_sessions.append(scripted_session)
        return scripted_session


factory = MultisessionFactory
