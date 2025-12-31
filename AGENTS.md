# ftputil Development Guide for Coding Agents

## Build/Test Commands
- **Run fast tests**: `make test` or `python -m pytest -m "not slow_test" test`
- **Run all tests**: `make all_tests` or `python -m pytest test`  
- **Run single test**: `python -m pytest test/test_<module>.py::<TestClass>::<test_method>`
- **Run with coverage**: `py.test --cov ftputil --cov-report html test`
- **Lint code**: `make pylint` or `pylint --rcfile=pylintrc ftputil/*.py`
- **Build distribution**: `make dist`
- **Run tox (multi-version testing)**: `tox`

## Code Style Guidelines
- **Max line length**: 88 characters (follows pylintrc config)
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
- Use `scripted_session` for FTP session mocking
- Dependencies: pytest, freezegun (see tox.ini)