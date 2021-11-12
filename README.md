# Celestial: Videoconferencing Evaluation

This repository contains the example application we use to evaluate Celestial.
Check out [the main repository](https://github.com/OpenFogStack/Celestial) to
learn more about Celestial!

## Application

There are three clients, a tracker, and a number of satellite (or cloud) servers.

### Client

The clients are based on Matthew Rahtz' [ultra_ping](https://github.com/mrahtz/ultra_ping)
utility, which we heavily modified for our use case.

It sends UDP packets based on the included `workload.csv` WebRTC traces.

### Tracker

The tracker selects an optimal satellite server and instructs clients to send
their data to that server.

### Server

The server forwards UDP packets to the three clients and duplicates incoming packets.
This is based on `NFTables`.

## Evaluation

We include several _Jupyter_ notebooks in this repository to help you analyze and
graph your results.

## Usage

To try out the videoconferencing evaluation, you need:

- a Celestial testbed including a Coordinator with database features enabled
- the Celestial `rootfsbuilder` Docker image built
- Docker
- go version >=1.16 installed and on your `PATH`
- `make`
- the ability to configure and build Linux kernels (see the Celestial's
    documentation for more information on this)

### Building Root Filesystems

First, build the root filesystems for the three components.
Simply use `make` to build everything.
You will end up with `tracker.img`, `alt-tracker.img`, `server.img`, and
`client.img` in this folder.

### Building Kernel

Use the `client/client-kernel.config` and `server/server-kernel.config` to
build `client-linux.bin` and `server-linux.bin` Linux kernels.
Note that using off-the-shelf kernels will not work in most situations since
the server needs support for `NFTables` duplication and clients need to trust
the host's randomness pool.

### Copying Everything Over

Make sure that your Celestial hosts have all root filesystems and kernels in their
`/celestial` directory.

### Configuring Configuration Files

Depending on your setup, you may need to adapt the included Celestial configuration
files.
There is `videoconference-cloud.toml` for the cloud-based application and
`videoconference-satellite.toml` for the satellite server based application.
Make sure that all host addresses and your Coordinator's address for the database
are set correctly.
