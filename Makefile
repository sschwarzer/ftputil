# Copyright (C) 2003-2017, Stefan Schwarzer <sschwarzer@sschwarzer.net>
# and ftputil contributors (see `doc/contributors.txt`)
# See the file LICENSE for licensing terms.

# This Makefile requires GNU Make.

SHELL=/bin/sh
PROJECT_DIR=$(shell pwd)
VERSION=$(shell cat VERSION)
PYTHON_BINARY?=python3
PYTEST=${PYTHON_BINARY} -m pytest

TEST_DIR=${PROJECT_DIR}/test

SOURCE_DIR=${PROJECT_DIR}/ftputil

DOC_DIR=${PROJECT_DIR}/doc
STYLESHEET_PATH=${DOC_DIR}/default.css
DOC_SOURCES=$(subst d/,${DOC_DIR}/, d/ftputil.txt \
			  d/whats_new_in_ftputil_3.0.txt \
			  d/whats_new_in_ftputil_4.0.0.txt)
DOC_TARGETS=$(subst d/,${DOC_DIR}/, d/ftputil.html \
			  d/whats_new_in_ftputil_3.0.html \
			  d/whats_new_in_ftputil_4.0.0.html)

SED=sed -i'' -r -e

PYTHONPATH=${PROJECT_DIR}:${TEST_DIR}

# TODO: Some platforms call that script rst2html.py - allow both.
RST2HTML=rst2html

# Name test files. Make sure the long-running tests come last.
TEST_FILES=$(shell ls -1 ${TEST_DIR}/test_*.py | \
			 grep -v "test_real_ftp.py" | \
			 grep -v "test_public_servers.py" ) \
		   ${TEST_DIR}/test_real_ftp.py \
		   ${TEST_DIR}/test_public_servers.py


# Put this first to avoid accidental patching if running `make`
# without target.
.PHONY: dummy
dummy:

# Patch various files to refer to a new version.
.PHONY: patch
patch:
	@echo "Patching files"
	${SED} "s/^__version__ = \".*\"/__version__ = \"${VERSION}\"/" \
		${SOURCE_DIR}/version.py
	${SED} "s/^:Version:   .*/:Version:   ${VERSION}/" \
		${DOC_DIR}/ftputil.txt
	${SED} "s/^:Date:      .*/:Date:      `date +"%Y-%m-%d"`/" \
		${DOC_DIR}/ftputil.txt
	${SED} "s/^Version: .*/Version: ${VERSION}/" PKG-INFO
	${SED} "s/(\/wiki\/Download\/ftputil-).*(\.tar\.gz)/\1${VERSION}\2/" \
		PKG-INFO

# Documentation
vpath %.txt ${DOC_DIR}

.PHONY: docs
docs: ${DOC_SOURCES} ${DOC_TARGETS}

%.html: %.txt
	${RST2HTML} --stylesheet-path=${STYLESHEET_PATH} --embed-stylesheet $< $@

# Quality assurance
.PHONY: test
test:
	@echo -e "=== Running fast tests for ftputil ${VERSION} ===\n"
	${PYTEST} -m "not slow_test" test

# Alternative for symmetry with target `all_tests`
.PHONY: tests
tests: test

all_tests:
	@echo -e "=== Running all tests for ftputil ${VERSION} ===\n"
	${PYTEST} test

.PHONY: tox_test
tox_test:
	# Gets settings from `tox.ini`
	tox

.PHONY: coverage
coverage:
	py.test --cov ftputil --cov-report html test

.PHONY: pylint
pylint:
	pylint --rcfile=pylintrc ${PYLINT_OPTS} ${SOURCE_DIR}/*.py | \
		less --quit-if-one-screen

.PHONY: find_missing_unicode_literals
find_missing_unicode_literals:
	find ftputil test -name "*.py" \
	  -exec grep -L "from __future__ import unicode_literals" {} \;

# Make a distribution tarball.
.PHONY: dist
dist: clean patch pylint docs
	${PYTHON_BINARY} setup.py sdist

.PHONY: extdist
extdist: all_tests dist upload

# Upload package to PyPI.
# See also https://packaging.python.org/tutorials/packaging-projects/
.PHONY: upload
upload:
	@echo "Uploading new version to PyPI"
	${PYTHON_BINARY} -m twine upload Dist/ftputil-${VERSION}.tar.gz

# Remove files with `orig` suffix (caused by `hg revert`).
.PHONY: cleanorig
cleanorig:
	find ${PROJECT_DIR} -name '*.orig' -exec rm {} \;

# Remove generated files (but no distribution packages).
.PHONY: clean
clean:
	rm -f ${DOC_TARGETS}
	# Use absolute path to ensure we delete the right directory.
	rm -rf ${PROJECT_DIR}/build
	find ${PROJECT_DIR} -type f -name "*.pyc" -exec rm {} \;
	find ${PROJECT_DIR} -type d -name "__pycache__" -exec rm -r {} \;

# Help testing test installations. Note that `pip uninstall`
# doesn't work if the package wasn't installed with pip.
.PHONY: remove_from_env
remove_from_env:
	rm -rf ${VIRTUAL_ENV}/doc/ftputil
	rm -rf ${VIRTUAL_ENV}/lib/python3.*/site-packages/ftputil

# For integration tests in `test_real_ftp.py`
DOCKER?=docker
IMAGE?=sschwarzer/ftputil-test-server:0.2
CONTAINER?=test_server_container

.PHONY: build_test_server_image
build_test_server_image:
	${DOCKER} image build -t ${IMAGE} test_server
	#${DOCKER} image rm $(shell ${DOCKER} image ls -q --filter="dangling=true")

.PHONY: run_test_server
run_test_server: build_test_server_image
	# If container exists, remove it.
	if [ ! -z "$(shell ${DOCKER} container ls -q --filter name=${CONTAINER})" ]; then \
		${DOCKER} container rm -f ${CONTAINER}; \
	fi
	${DOCKER} container run --rm --detach --name ${CONTAINER} \
		-p 127.0.0.1:2121:21 -p 127.0.0.1:30000-30009:30000-30009 ${IMAGE}
