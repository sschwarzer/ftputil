# Test server for ftputil integration tests

The test file `test_real_ftp.py` uses a local FTP server.

This Dockerfile and data provide a Docker container that contains the FTP
server and the data to test against.

When in the `test_server` directory, build the image with
```
docker image build -t ftputil-test-server:0.1 .
```

The pre-built image is also available from the Docker Hub via
```
docker pull sschwarzer/ftputil-test-server:0.1
```

Run the container with
```
docker container run --rm --detach --name test-server-container \
  -p 2121:21 -p 30000-30009:30000-30009 sschwarzer/ftputil-test-server:0.1
```

The port 2121 is expected by the tests in `test_real_ftp.py`. If the port 2121
is already used on your computer, you can change the port in the above
container creation and edit the `PORT` variable in `test_real_ftp.py`
accordingly.

**WARNING: The included FTP server is solely for local tests. I made no efforts
to make it secure.**
