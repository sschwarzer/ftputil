# Copyright (C) 2018, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.


__all__ = ["Call", "ScriptedSession", "factory"]


class Call:

    def __init__(self, method_name, result=None, args=None, kwargs=None):
        self.method_name = method_name
        self.result = result
        self.args = args if args is not None else ()
        self.kwargs = kwargs if kwargs is not None else {}


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
        # Always expect an entry for the constructor.
        init = script[0]
        assert init.method_name == "__init__"
        if isinstance(init.result, Exception) or self._is_exception_class(init.result):
            # Simulate an exception raised in the factory's constructor.
            raise init.result
        self.script = script[1:]
        self._script_iter = iter(self.script)

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

    def __getattr__(self, attribute_name):
        print("attribute name:", attribute_name)
        call = next(self._script_iter)
        print("calling {0.method_name!r} with result {0.result!r}".format(call))
        assert call.method_name == attribute_name, (
                 "called method {!r} instead of {!r}".format(attribute_name,
                                                             call.method_name))
        def dummy_method(*args, **kwargs):
            if isinstance(call.result, Exception) or self._is_exception_class(call.result):
                raise call.result
            else:
                return call.result
        return dummy_method


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
