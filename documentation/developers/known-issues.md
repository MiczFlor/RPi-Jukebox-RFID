# Known Issues

## Legacy custom libzmq installation

Current releases use the Raspberry Pi OS or Debian `libzmq5` and
`python3-zmq` packages. The installer deliberately does not delete files
under `/usr/local`.

An installation upgraded from an older release may still have the project's
custom libzmq archive under `/usr/local`. First check which library is loaded:

```bash
ldconfig -p | grep libzmq
python3 -c 'import zmq; print(zmq.__file__, zmq.zmq_version())'
```

Only if the old archive is known to have been installed by Phoniebox, its
libzmq-specific files can be removed before refreshing the linker cache:

```bash
sudo rm -f /usr/local/lib/libzmq.so*
sudo rm -f /usr/local/lib/pkgconfig/libzmq.pc
sudo rm -f /usr/local/include/zmq.h /usr/local/include/zmq_utils.h
sudo rm -rf /usr/local/lib/cmake/ZeroMQ
sudo ldconfig
```

Do not remove unrelated files from `/usr/local`.

## Configuration

In `jukebox.yaml` (and all other config files):
Always use relative path from folder `src/jukebox` (`../../`), but do not use relative paths with `~/`.

**Sole** exception is in `playermpd.mpd_conf`.
