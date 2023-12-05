# Known Issues

## Installing limzmq in Docker fails

To speed up the Docker build process, we are distributing pre-build versions of libzmq with drafts flag at the latest version. In case the download fails because the respective architecture build does not exist, you can build the version yourself. Just replace the command to download the pre-built library with the following command

```
# Compile ZMQ
RUN cd ${HOME} && mkdir ${ZMQ_TMP_DIR} && cd ${ZMQ_TMP_DIR}; \
    wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz; \
    tar -xzf libzmq.tar.gz; \
    rm -f libzmq.tar.gz; \
    zeromq-${ZMQ_VERSION}/configure --prefix=${ZMQ_PREFIX} --enable-drafts; \
    make && make install
```

## Configuration

In `jukebox.yaml` (and all other config files): do not use relative paths with `~/some/dir`.
Always use entire explicit path, e.g. `/home/pi/some/dir`.

**Sole** exception is in `playermpd.mpd_conf`.
