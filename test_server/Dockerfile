# Dockerfile to set up the test server for running `test_real_ftp.py`
#
# Note that since we use this only for testing, we don't need to persist data
# across container recreations.

FROM stilliard/pure-ftpd

# 1000 already exists
ARG UID=1001
ARG USERNAME=ftptest
# This container is only supposed to run locally for testing!
ARG PASSWORD=dummy

# See https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL net.sschwarzer.ftputil.authors="Stefan Schwarzer"

COPY ./pure-ftpd.conf /etc/pure-ftpd/

RUN \
  # Regarding the home directory: I wanted to use `/home/ftpusers/ftptest`, but
  # the image we inherit from makes `/home/ftpusers` a volume, so if we create
  # directories or files there they won't be visible when the container is
  # started.
  #
  # The user needs a shell for Unix authentication.
  useradd --gid=ftpgroup --uid=${UID} --home-dir=/home/${USERNAME} \
          --create-home --shell=/bin/bash ${USERNAME} && \
  echo "${USERNAME}:${PASSWORD}" | chpasswd && \
  # Use only configuration from overwritten `pure-ftpd.conf`
  rm /etc/pure-ftpd/conf/*

CMD pure-ftpd -l unix -E -j -P localhost -p 30000:30009 -c 5 -C 5
