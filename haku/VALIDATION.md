# Validation

Validated on 2026-10-21: iPhone 12 (`iPhone13,2`), iOS 16.1.1, Dopamine rootless.
The package is `iphoneos-arm64`, uses `/var/jb`, and has deployment target iOS
15.0. Its server executable contains both arm64 and arm64e slices. Other
devices/OS versions and non-PAC execution remain untested.

The package installs and controls only `com.jacklee.haku-server`. Its default
listener is loopback `57042`; the package launcher always uses the configured
port. It does not modify the existing Frida package or its launchd service.

## 17.24.3+haku.2 with Haku 0.2.2

The final installed pair was validated on **2026-10-21**. The server is built
from `1a30e4b07c059a22787b27c257baf74ee63e54b3`, with Frida wire protocol
17.24.3 and the opt-in boolean `haku-background` launch option. Runtime branding
reports `17.24.3+haku.2`. Its clean universal build and all-architecture Apple
ad-hoc signature verification passed; **9** maintained host checks passed, and
the [GitHub source-build run passed](https://github.com/JackLee992/haku-server/actions/runs/39542534072).
See [BACKGROUND-LAUNCH.md](BACKGROUND-LAUNCH.md) for launch semantics.

The physical Haku GUI regression selected a small-range encrypted target with
active search, kept Haku active in all **33** samples, completed export and
presented the share sheet in **9.529 seconds**. It restored the prior idle
setting and ended its finite background task. This directly verifies the
background launch behavior that CLI acquisition alone could not establish.
The test invokes real UIKit callbacks; physical touch and XCTest are separate.

The app's Mach-O independently declares **4,096 encrypted bytes**. Haku copies
**20,628,414 bytes** of complete app files and exports a **16,297,676-byte IPA**.
All **60** ZIP members pass independent CRC checks. The **4,886,128-byte** main
image passes the independent transition comparator, and a new original process
read through the unchanged upstream USB Frida service produces the exact same
4,096 plaintext bytes. The already-clear framework matches its original file.
Thus the small captured count is corroborated by both metadata and contents.

A full final-pair export also passed at **58000**, with the old default port
rejecting connections. Default **57042** was restored afterward. The original
Frida daemon PID and binary hash were unchanged across installation. Haku Mac's
shared core exported/retrieved the small IPA with independent local SHA-256/ZIP
checks and cancelled a larger export through its exact CLI worker PID, leaving
a `cancelled` report and no finished IPA. See the
[matching sanitized record](validation/2026-10-21-0.2.2.json),
[Sileo guide](INSTALLATION.md) and [port guide](PORTS.md).

A separate development-signed QA copy passed normal iOS installation. Both it
and an ordinary fresh launch of the installed original produced white USB
screenshots for 30 seconds. A separate read-only diagnostic confirmed an active
QA process, responsive main queue and populated SwiftUI view tree. Explicit
screenshot-protection code is present, which is consistent with capture privacy;
visible content and app functionality remain unverified. Signing/installation
and process activation were tested separately from acquisition. No capture
protection was disabled. Raw captures and identifiers remain private. Sileo
import remains manual acceptance.

## Reproducibility rerun and Haku 0.2.1

The installed-suite rerun on **2026-10-21 (Asia/Shanghai)** used Haku 0.2.0 at
the restored default endpoint `127.0.0.1:57042`. It completed in **32 seconds**:
33 encrypted images verified, 2 already clear, 235,618,304 bytes captured, and
all 1,383 ZIP members independently checked. The IPA SHA-256 exactly matched
the preceding custom-port export. Every native image record matched the earlier
Haku 0.2.0 and 0.1.0 runs; the independent main Mach-O comparison also passed.
The installed originals, both server executables and both daemon PIDs remained
unchanged. No private capture artifacts were published.

The subsequent **Haku 0.2.1** package removes bundle-ID, prefix and fixed
installation-directory filters and adds the manga chestnut icon. It uses this
same server release and protocol. Final package checks on the same phone showed:

| Haku 0.2.1 integration gate | Result |
| --- | --- |
| Client/server host checks | 25 client checks and 8 maintained-server checks passed |
| Unfiltered discovery | 44 applications, including 37 Apple applications |
| Previous encrypted target | Fully verified in 33 seconds; 35 native images and 1,383 ZIP entries; IPA hash identical to 0.2.0 |
| Owner-built lab app | Fully verified export; 1 already-clear image and 29 ZIP entries |
| Apple-prefix system app (Calculator) | Fully verified export; 1 already-clear image and 59 ZIP entries |
| Rootless Haku app from a separate CLI worker | Fully verified export; 1 already-clear image and 10 ZIP entries |
| Target restart/cleanup | Client confirms process exit with a bounded exact-PID termination check; final running-app case passed |
| Original files and services | Original native hashes, both server hashes and both daemon PIDs unchanged |
| GUI/Sileo interaction | Local-deb import, Haku GUI capture and share-sheet touch checks remain manual |

The extra clear-image cases are export coverage checks; they do not count as
additional decrypted encrypted images. Other applications still depend on OS
permissions, Frida launch support and loaded-image coverage.

The client package SHA-256 is
`61d75cac40a54ff45f3cc3b47fb67dd6aed70a179956f1434b8d6eb4956aced7`,
built from client revision `e79d1f316913f73d0332aa87d58b6745ce7e9c22`.
The server release package remains
`25c0844918bdedc0a3ddfd981bc55294cddf3e33562b63e618d3672ba5a1ec77`.
See the [matching sanitized validation JSON](validation/2026-10-21.json),
[Sileo installation guide](INSTALLATION.md), and [port guide](PORTS.md).

## Server release acceptance

| Gate | Result |
| --- | --- |
| Host package, shell port, asynchronous restart and branded-tag version checks | 8 passed |
| Haku client integrity and connection checks | 21 passed |
| Universal source build and all-architecture signature verification | Passed |
| Rootless package install, service start and application enumeration | Passed |
| Default 57042 and custom 58000 connections | Passed |
| Invalid and reserved Frida ports; conflicting listen options | Rejected |
| App preference persistence across fresh processes | Passed |
| Server restart and package upgrade with custom port | Passed; 58000 preserved |
| Connection to old port after change | Failed as expected; no fallback to Frida |
| End-to-end export through custom port 58000 | Passed; 33 encrypted images verified, 2 originally clear, 235,618,304 bytes captured |
| Independent archive check | All 1,383 members passed Python ZIP CRC checks |
| Independent main-executable comparison | Passed; encryption ranges changed and stable bytes/identity preserved; hash matches prior validated acquisition |
| Original installed app and ordinary Frida executable | Hashes unchanged; original Frida PID unchanged and enumeration still works |
| Final configuration | Client and daemon restored to 57042; both services operational |
| Hands-on Connection screen and GUI export/share | Deferred to owner; no manual UI acceptance inferred |

Capture-tested implementation revision: `43c78d33d98d6427beeaede87bd239929215ced6`.
The release artifact's build revision is recorded in its `build.json`.
Server executable SHA-256:
`d1bcb2ab814137f101c996b8f59fd20f23b676f653fb7b501867017bee2084fa`.
This exact executable passed the full export test. The final package additionally
passed port-change, restart, configuration-preservation and coexistence checks.

The first thin build enumerated applications but could not complete app startup.
The final build includes both server architectures and their embedded payloads,
with native Apple ad-hoc signatures. A separate rootless launchd regression
required an explicit shell program and waiting for asynchronous service removal
before re-registering it. These are covered by host and device checks.

The tagged prerelease contains locally built, device-validated assets and build
metadata. Existing release assets are preserved by reruns of the publishing job.
GitHub Actions validates source builds separately; it does not run physical iOS
or GUI tests. Acquisition validation does not establish signing, reinstallation,
ordinary launch or functional behavior of an exported application.

The initial release tag exposed upstream version discovery rejecting the
`haku-v` prefix. The maintained branch now reads the core project version from
the pinned protocol manifest, with a regression check. The published prerelease
assets remain the locally built and device-validated artifacts above.
