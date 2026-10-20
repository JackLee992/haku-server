# Validation

Validated on 2026-10-21: iPhone 12 (`iPhone13,2`), iOS 16.1.1, Dopamine rootless.
The package is `iphoneos-arm64`, uses `/var/jb`, and has deployment target iOS
15.0. Its server executable contains both arm64 and arm64e slices. Other
devices/OS versions and non-PAC execution remain untested.

The package installs and controls only `com.jacklee.haku-server`. Its default
listener is loopback `57042`; the package launcher always uses the configured
port. It does not modify the existing Frida package or its launchd service.

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
