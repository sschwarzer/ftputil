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
COPY ./${USERNAME} /home/ftptest/

RUN \
  # Regarding the home directory: I wanted to use `/home/ftpusers/ftptest`, but
  # the image we inherit from makes `/home/ftpusers` a volume, so if we create
  # directories or files there they won't be visible when the container is
  # started.
  #
  # The user needs a shell for PureFTPd unix authentication to work.
  useradd --gid=ftpgroup --uid=${UID} --home-dir=/home/${USERNAME} \
          --no-create-home --shell=/bin/bash ${USERNAME} && \
  echo "${USERNAME}:${PASSWORD}" | chpasswd && \
  # Use only configuration from overwritten `pure-ftpd.conf`.
  rm /etc/pure-ftpd/conf/* && \
  # Fix owner/group settings.
  cd /home/${USERNAME} && \
  chown -R root:root . && \
  chown ${USERNAME}:ftpgroup . rootdir2/dir2 && \
  # Remove `.emtpy` markers.
  find . -name ".empty" -exec rm {} \;

EXPOSE 2121

# Without the `sleep` command, the FTP server goes into the background
# and the container exits immediately.
CMD pure-ftpd /etc/pure-ftpd/pure-ftpd.conf && sleep infinity
