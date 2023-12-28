#An extra layer to get around this bug https://github.com/docker/buildx/issues/395
#It's there simply to download add required libraries for cargo build
FROM --platform=$BUILDPLATFORM rust:bullseye AS rust_fix

ENV USER=root
ENV V_spotifyd=v0.3.5

WORKDIR /usr/src/spotifyd
RUN apt-get -y update && \
    apt-get install --no-install-recommends -y apt-transport-https ca-certificates git && \
    git clone --depth 1 --branch=${V_spotifyd} https://github.com/Spotifyd/spotifyd.git .

# Don't do `cargo init` or --> error: `cargo init` cannot be run on existing Cargo packages
# RUN cargo init
RUN mkdir -p .cargo \
  && cargo vendor > .cargo/config

FROM rust:bullseye as build

RUN apt-get -y update && \
    apt-get install --no-install-recommends -y libasound2-dev build-essential pulseaudio libpulse-dev libdbus-1-dev

COPY --from=rust_fix /usr/src/spotifyd /usr/src/spotifyd
WORKDIR /usr/src/spotifyd

RUN cargo build -j 2 --release --features pulseaudio_backend,dbus_mpris --offline

FROM debian:bullseye-slim as release

CMD ["dbus-run-session", "/usr/bin/spotifyd", "--no-daemon"]

RUN apt-get update && \
    apt-get install -yqq --no-install-recommends libasound2 pulseaudio dbus libssl1.1 && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r spotify && \
    useradd --no-log-init -r -g spotify -G audio spotify

COPY --from=build /usr/src/spotifyd/target/release/spotifyd /usr/bin/

USER spotify
