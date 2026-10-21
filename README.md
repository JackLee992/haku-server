# haku-server

Haku's maintained source fork of [Frida Core](https://github.com/frida/frida-core),
based on **17.24.3**, for rootless iOS. It supplies Haku with its own executable,
Debian package, launchd service and loopback port configuration.

| Setting | haku-server | Ordinary Frida |
| --- | --- | --- |
| Default endpoint | `127.0.0.1:57042` | `127.0.0.1:27042` |
| Package | `com.jacklee.haku-server` | `re.frida.server` |
| launchd label | `com.jacklee.haku-server` | `re.frida.server` |
| Executable | `/var/jb/usr/sbin/haku-server` | Separate upstream installation |

The package neither replaces nor stops the upstream Frida service. Haku port
settings reject `27042` and `27043` to keep them separate. The Frida **17.24.3
wire protocol** remains compatible. This fork changes naming, configuration and
packaging, and an opt-in background app launcher. Use it only on devices and applications you own or are authorized to
assess.

## Install and configure

Download the rootless `.deb` from the
[17.24.3+haku.2 release](https://github.com/JackLee992/haku-server/releases/tag/haku-v17.24.3-haku.2),
save it to Files on the phone, and use **Share → Sileo** to install it. Complete
the server installation before installing **Haku 0.2.2**. Upgrade both components together; older clients pin haku.1. Both default to port `57042`.

**[Complete Sileo installation](haku/INSTALLATION.md) ·
[Custom-port guide](haku/PORTS.md) · [Validation results](haku/VALIDATION.md)**

The Haku client repository is currently private; its downloads require access.
There is no hosted Haku APT source, so GitHub URLs should not be entered as
Sileo source addresses. The local-package installation flow and terminal
alternative are documented in the installation guide.

To change the daemon's port, run as root on the phone:

```sh
hakuctl port 58000
hakuctl status
```

Then enter **58000** in **Haku > Connection > Port > Save**. The app's setting is
its connection destination; `hakuctl` changes and restarts the daemon. Configuration
is stored as data in `/var/jb/etc/haku-server.port` and preserved across upgrades.
`hakuctl port` reads the current value. `start`, `stop`, and `restart` control only
the Haku service.

Run Haku's `--set-port` commands as **mobile** to configure the GUI user's
preference. A one-command `Haku --port PORT --list` override does not change
the daemon or the saved client preference. See the port guide for complete
examples, a default reset and optional SSH forwarding.

For a manually managed instance, `haku-server --port 58000` binds to loopback.
Upstream `--listen ADDRESS`, TLS and token options remain available; use an
explicit port with `--listen`. `--port` and `--listen` are mutually exclusive.
`--haku-info` prints the fork identity, pinned upstream revision and protocol
version as JSON. `--version` reports `17.24.3+haku.2`.

## Build from source

Requirements: Apple Silicon macOS, Xcode 26.5+ with iPhoneOS SDK, Python 3.10+,
Node.js 18+ and the Xcode command-line tools.

```sh
git clone --branch haku https://github.com/JackLee992/haku-server.git
cd haku-server
git submodule update --init --recursive
python3 -m unittest discover -s haku/tests -v
python3 haku/build.py
```

The upstream build system fetches its versioned toolchain/dependency SDKs and
the pinned Frida Gum source. The server, helper and agent are compiled from
source for arm64 and arm64e. The build combines the server slices into a
universal executable and uses Apple's ad-hoc signing with
`server/haku-server.xcent`, including an all-architecture signature check.
Output is `dist/com.jacklee.haku-server_17.24.3+haku.2_iphoneos-arm64.deb`
and `dist/build.json`, including source and binary hashes and submodule revisions.

This package targets iOS 15+ rootless `/var/jb`, with arm64 and arm64e server
slices and embedded helper/agent payloads for iOS app startup. Other jailbreak layouts, system
targets and other device/OS combinations have not been validated. See
[validation](haku/VALIDATION.md) for the measured acceptance boundary.

## Maintenance and license

The `haku` branch is the maintained product branch. Keep changes small against
the upstream tag recorded in [haku/upstream.json](haku/upstream.json), updating
the matching Haku client devkit and server dependency together. Upstream remains
available at `https://github.com/frida/frida-core`; retain its history and license
notices when updating the base. The original README and CI configuration are
retained in [haku/README.upstream.md](haku/README.upstream.md) and
[haku/upstream-ci.yml](haku/upstream-ci.yml).

GitHub Actions builds the rootless package on macOS 26 with Xcode 26.5 and
publishes tagged prereleases. Physical-device tests are separate from CI.
Local release validation is recorded explicitly.

The [background launch extension](haku/BACKGROUND-LAUNCH.md) documents the
opt-in capture behavior used by Haku 0.2.2. The separate
[Haku Mac extension](https://github.com/JackLee992/haku-mac) provides a native
desktop controller and pins this repository as a submodule; it requires access
to that private client repository.

Frida Core and these modifications are under the upstream terms in
[COPYING](COPYING). Frida dependency notices remain in their original sources.
No real application captures, credentials or device identifiers belong here.
