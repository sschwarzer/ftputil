# Copyright (C) 2003-2019, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

import io

import ftputil


# Since `io.BytesIO` and `io.StringIO` are built-in, they can't be patched with
# `unittest.mock.patch`. However, derived classes can be mocked. Mocking is
# useful to test the arguments of `write` calls, i. e. whether the expected
# data was written.
class MockableBytesIO(io.BytesIO):
    pass


class MockableStringIO(io.StringIO):
    pass


# Factory to produce `FTPHost`-like classes from a given `FTPHost` class and
# (usually) a given `MockSession` class.
def ftp_host_factory(session_factory, ftp_host_class=ftputil.FTPHost):
    return ftp_host_class(
        "dummy_host", "dummy_user", "dummy_password", session_factory=session_factory
    )


def dir_line(
    mode_string="-r--r--r--",
    nlink=1,
    user="dummy_user",
    group="dummy_group",
    size=512,
    date_=None,
    datetime_=None,
    name="dummy_name",
    link_target=None,
):
    """
    Return a line as it would be returned by an FTP `DIR` invocation.

    Some values are handled specially:

    - One of `date_` or `datetime_` must be given, the other must be `None`.

      If `date_` is given, it must be a `datetime.date` object. The timestamp
      in the `DIR` line is formatted like "Apr 22 2019", with the concrete
      value taken from the `date_` object.

      If `datetime_` is given, it must be a `datetime.datetime` object. The
      timestamp in the `DIR` line is formatted like "Apr 22 16:50", with the
      concrete value taken from the `datetime_` object. Timezone information in
      the `datetime_` object is ignored.

    - If `link_target` is left at the default `None`, the name part is the
      value from the `name` argument. If `link_target` isn't `None`, the name
      part of the `DIR` line is formatted as "name -> link_target".

    Note that the spacing between the parts of the line isn't necessarily
    exactly what you'd get from an FTP server because the parser in ftputil
    doesn't take the exact amount of spaces into account, so the `DIR` lines
    don't have to be that accurate.

    Examples:

      # Result:
      # "drwxr-xr-x  2  dummy_user dummy_group  182  Apr 22 16:50  file_name"
      line = dir_line(mode_string="-rw-rw-r--",
                      nlink=2,
                      size=182,
                      datetime=datetime.datetime.now(),
                      name="file_name")

      # Result:
      # "drwxr-xr-x  1  dummy_user dummy_group  512  Apr 22 2019  dir_name -> dir_target"
      line = dir_line(mode_string="drwxr-xr-x",
                      date=datetime.date.today(),
                      name="dir_name",
                      link_target="dir_target")
    """
    # Date or datetime. We must have exactly one of `date_` and `datetime_`
    # set. The other value must be `None`.
    assert [date_, datetime_].count(
        None
    ) == 1, "specify exactly one of `date_` and `datetime_`"
    if date_:
        datetime_string = date_.strftime("%b %d %Y")
    else:
        datetime_string = datetime_.strftime("%b %d %H:%M")
    # Name, possibly with link target
    if not link_target:
        name_string = name
    else:
        name_string = "{} -> {}".format(name, link_target)
    #
    return "{}  {}  {} {}  {}  {}  {}".format(
        mode_string, nlink, user, group, size, datetime_string, name_string
    )
