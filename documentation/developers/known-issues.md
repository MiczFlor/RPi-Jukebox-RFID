# Known Issues

## Installing `libzmq` in Docker fails

To speed up the Docker build process, we are distributing pre-build versions of libzmq with drafts flag at the latest version. In case the download fails because the respective architecture build does not exist, you can build the version yourself.

Add `build-essential` to be installed additionally with `apt-get`. Additionally, replace the command to download the pre-built library with the following command.

```docker
# Compile ZMQ
RUN cd ${HOME} && mkdir ${ZMQ_TMP_DIR} && cd ${ZMQ_TMP_DIR}; \
    wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz; \
    tar -xzf libzmq.tar.gz; \
    rm -f libzmq.tar.gz; \
    zeromq-${ZMQ_VERSION}/configure --prefix=${ZMQ_PREFIX} --enable-drafts; \
    make && make install
```

[libzmq details](./libzmq.md)

## Configuration

In `jukebox.yaml` (and all other config files):
Always use relative path from folder `src/jukebox` (`../../`), but do not use relative paths with `~/`.

**Sole** exception is in `playermpd.mpd_conf`.
