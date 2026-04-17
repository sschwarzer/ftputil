# ftputil 5.2.0

Add deprecation warnings for backward-incompatible changes coming in ftputil
6.0.0.

- [x] Raise a `DeprecationWarning` once when ftputil is imported:
      "in ftputil 6.0.0, the default file path encoding will become UTF-8
      instead of Latin-1"

- [ ] Raise a `DeprecationWarning` for the removal of `FTPHost.path.walk`.
      In the future, `FTPHost.walk` should be used.

- [ ] Add the new constant `UNSET_TIME_SHIFT = object()` in
      `ftputil.host`. If ftputil accesses the time shift, print a
      `DeprecationWarning` once and set the time shift to 0.0 (the
      default value in ftputil 5.1.0). See [ticket #160][160].

      Deprecation message: "in ftputil 6.0.0, the time shift must be set
      with `set_time_shift` or `synchronize_times` to get timestamp stat
      data or to use `upload_if_newer` or `download_if_newer`"

- [ ] For changing file system APIs (see below), print a
      `DeprecationWarning` in each API function/method that is going to
      change with a change in the semantics.

      Print one warning for each site that calls the changing ftputil
      APIs. See [ticket #162][162]. For each of the changing APIs,
      print how the API will change (e.g. which argument defaults will
      be changed). Example: "in ftputil 6.0.0, the argument `xxx` will
      change its default value from `yyy` to `zzz`".

      Print the warnings unless we can be sure that the behavior for
      the call would be the same in ftputil 5.2.0 and 6.0.0.



# ftputil 6.0.0

ftputil 6.0.0 will require _at least_ Python 3.10.

- [ ] Update `FTPHost` (including `stat` namespace) to use up to date APIs.
      Occasionally, Python changes defaults or adds new arguments. Agentic
      coding should help with this.

- [ ] Switch default _file path_ encoding to UTF-8 (see [ticket #162][162])

- [ ] Revise handling of datetime parsing (see [ticket #160][160])
    - [ ] Add constant for unset timeshift
    - [ ] Use this constant as initial value for the timeshift
    - [ ] If this special value is set and a stat instance is requested,
          set the timestamp to `None`.
    - [ ] If this special value is set and `upload_if_newer` or
          `download_if_newer` are used, raise an exception.
    - [ ] If the timeshift has been set with `set_time_shift` or `synchronize_times`,
          behave as currently.


[162]: https://todo.sr.ht/~sschwarzer/ftputil/162 "Change file path encoding to UTF-8"
[160]: https://todo.sr.ht/~sschwarzer/ftputil/160 "Feb 29 Error -- ValueError: day is out of range for month"
