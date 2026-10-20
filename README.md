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
packaging. Use it only on devices and applications you own or are authorized to
assess.

## Install and configure

Install the `.deb` from [Releases](https://github.com/JackLee992/haku-server/releases)
with Sileo, then install Haku 0.2.0 or later. Both default to port `57042`.

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

For a manually managed instance, `haku-server --port 58000` binds to loopback.
Upstream `--listen ADDRESS`, TLS and token options remain available; use an
explicit port with `--listen`. `--port` and `--listen` are mutually exclusive.
`--haku-info` prints the fork identity, pinned upstream revision and protocol
version as JSON. `--version` reports `17.24.3+haku.1`.

## Build from source

Requirements: Apple Silicon macOS, Xcode 26.5+ with iPhoneOS SDK, Python 3.10+,
Node.js 18+, make and `ldid` (`brew install ldid`).

```sh
git clone --branch haku https://github.com/JackLee992/haku-server.git
cd haku-server
git submodule update --init --recursive
python3 -m unittest discover -s haku/tests -v
python3 haku/build.py
```

The upstream build system fetches its versioned toolchain/dependency SDKs and
the pinned Frida Gum source. The server, helper and agent are compiled from
source. The build uses local ad-hoc signing, then `ldid` with
`server/haku-server.xcent`; `LDID` may name an absolute executable path.
Output is `dist/com.jacklee.haku-server_17.24.3+haku.1_iphoneos-arm64.deb`
and `dist/build.json`, including source and binary hashes and submodule revisions.

This package targets iOS 15+ rootless `/var/jb` and embeds arm64 and arm64e
helper/agent payloads for iOS app startup. Other jailbreak layouts, system
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

Frida Core and these modifications are under the upstream terms in
[COPYING](COPYING). Frida dependency notices remain in their original sources.
No real application captures, credentials or device identifiers belong here.
