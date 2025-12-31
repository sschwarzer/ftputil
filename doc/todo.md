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
