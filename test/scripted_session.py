# Copyright (C) 2018-2019, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.


__all__ = ["Call", "ScriptedSession", "factory"]


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

    def __init__(self, script):
        self.script = script
        # Index into `script`, the list of `Call` objects
        self._index = 0
        # Always expect an entry for the constructor.
        init = self._next_call(expected_method_name="__init__")
        init()

    def _print(self, text):
        """
        Print `text`, prefixed with a `repr` of the `ScriptedSession`
        instance.
        """
        print("<ScriptedSession at {}> {}".format(hex(id(self)), text))

    def _next_call(self, expected_method_name=None):
        """
        Return next `Call` object.

        Print the `Call` object before returning it. This is useful for
        testing and debugging.
        """
        self._print("Expected method name: {!r}".format(expected_method_name))
        call = self.script[self._index]
        self._index += 1
        self._print("Next call: {!r}".format(call))
        if expected_method_name is not None:
            assert call.method_name == expected_method_name, (
                     "called method {!r} instead of {!r}".format(expected_method_name,
                                                                 call.method_name))
        return call

    def __getattr__(self, attribute_name):
        call = self._next_call(expected_method_name=attribute_name)
        def dummy_method(*args, **kwargs):
            self._print("args: {!r}".format(args))
            self._print("kwargs: {!r}".format(kwargs))
            call.check_args(args, kwargs)
            return call()
        return dummy_method

    def dir(self, path, callback):
        """
        Call the `callback` for each line in the multiline string
        `call.result`.
        """
        call = self._next_call(expected_method_name="dir")
        for line in call.result.splitlines():
            callback(line)


def factory(script):
    """
    Return a session factory taking the scripted data from `script`.

    Use it like

      host = ftputil.FTPHost(host, user, password,
                             session_factory=scripted_session.factory(script))
    """
    # `ftputil.FTPHost` takes a `session_factory` argument. When the
    # `FTPHost` instance is used, the session factory will be called
    # with host, user and password arguments. However, since we want
    # to control the factory from a specific `script` that `FTPHost`
    # doesn't know about, return the actual factory that will be used
    # by the `FTPHost` instance.
    def session_factory(host, user, password):
        return ScriptedSession(script)
    return session_factory
