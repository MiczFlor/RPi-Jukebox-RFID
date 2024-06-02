# `libzmq` for Raspberry Pi

## `libzmp` Releases

The Jukebox requires `libzmq` to work properly. We provide downloadable builds to speed up the installation process of the Phoniebox.

* <https://github.com/pabera/libzmq/releases>

> [!NOTE]
> We can't use stable builds that are distributed by [zeromq](https://github.com/zeromq/libzmq/releases) directly because the Jukebox requires draft builds to support WebSockets. These [draft builds](https://pyzmq.readthedocs.io/en/latest/howto/draft.html) are not officially provided through zeromq for Raspberry Pi architecture (e.g. `armv6` or `armv7`).

## Building `libzmq`

If you need to update the `libzmq` version in the future, follow these steps.

### Install Cross-Compilation Environment

First, you need to install Dockcross. Dockcross provides Docker images for cross-compilation.

#### 1. Pull the Dockcross Image

For Raspberry Pi B, 4 or Zero 2 we need `linux-armv7`, for older models `linux-armv6`. The following example shows how to compile for `armv7` (32 bit, `arm32v7`). If you want to compile for another target, change the commands accordingly. For Docker Development environments, other targets like `arm64` or `x86_64` become relevant.

```bash
docker pull dockcross/linux-armv7
```

#### 2. Create a Dockcross Script

After pulling the image, you create a Dockcross script which will be used to run the cross-compilation tools in the Docker container.

```bash
docker run --rm dockcross/linux-armv7 > ./dockcross-linux-armv7
chmod +x ./dockcross-linux-armv7
```

This command creates a script named `dockcross-linux-armv7` in your current directory.

### Cross-Compiling libzmq

With Dockcross installed, you can now modify your `libzmq` compilation process to use the Dockcross environment.

#### 1. Download `libzmq` Source

Similar to your original process, download the `libzmq` source code:

```bash
ZMQ_VERSION=4.3.5
wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz
tar -xzf libzmq.tar.gz
```

#### 2. Cross-Compilation using Dockcross

Modify your build process to run inside the Dockcross environment:

```bash
./dockcross-linux-armv7 bash -c '\
cd zeromq-${ZMQ_VERSION} && \
./configure --prefix=/usr/local --enable-drafts && \
make -j$(nproc) && \
make install DESTDIR=$(pwd)/../installed'
```

> [!NOTE]
> In the script above, you need to update ${ZMQ_VERSION} to the actual value as the script does not jave access to your host machine ENV variables.

This command configures and builds `libzmq` inside the Docker container. The `DESTDIR` variable is used to specify where to install the files inside the container.

#### 3. Compress the Compiled Binaries

After compilation, the binaries are located in the `installed` directory inside your `zeromq-${ZMQ_VERSION}` directory.

```bash
tar -czvf libzmq5-armv7-${ZMQ_VERSION}.tar.gz -C installed/usr/local --exclude='.' include lib
```
