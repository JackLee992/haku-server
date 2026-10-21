# Install haku-server and Haku with Sileo

These are **rootless `iphoneos-arm64` packages** for an already activated
`/var/jb` jailbreak. Their deployment target is iOS 15.0 or later; physical
validation covers **iPhone 12 / iOS 16.1.1 / Dopamine rootless**. Other device,
OS and jailbreak combinations need their own testing.

| Order | Package | Version | Release |
| --- | --- | --- | --- |
| 1 | `com.jacklee.haku-server` | `17.24.3+haku.1` | [Server release](https://github.com/JackLee992/haku-server/releases/tag/haku-v17.24.3-haku.1) |
| 2 | `com.jacklee.haku` | `0.2.1` | [Haku release](https://github.com/JackLee992/haku/releases/tag/v0.2.1) |

Haku 0.2.0 and 0.2.1 both pin this exact server package and Frida protocol
17.24.3. The original upstream Frida service can coexist with Haku's daemon,
but does not replace Haku's dependency.

## Sileo local-package installation

1. Download the [server rootless .deb](https://github.com/JackLee992/haku-server/releases/download/haku-v17.24.3-haku.1/com.jacklee.haku-server_17.24.3%2Bhaku.1_iphoneos-arm64.deb)
   in Safari and save it to Files on the iPhone.
2. Use **Share → Sileo** from Files; look under **More** if necessary. Install
   the package and complete the Sileo queue and any requested restart action.
3. Download Haku's `.deb` from its release and install it the same way, after
   the server has finished installing.
4. Open Haku and refresh its application list. The fresh-install endpoint is
   `127.0.0.1:57042`; saved custom ports are retained during upgrades.

The Haku repository is **private**. Sign in to GitHub with an account that has
access before downloading the client. An unauthenticated 404 is not a missing
public release. The server repository and release are public.

Sileo's [official local-deb handler](https://github.com/Sileo/Sileo/blob/c9f70158a037dc76b91c450e72af2de0514dd3ee/Sileo/AppDelegate.swift#L218-L237)
opens a local package page. The physical package tests used terminal installation;
hands-on Sileo import and Haku GUI export/share remain separate manual checks.
There is currently **no hosted Haku APT source**. Use local release packages;
the GitHub repository and release URLs are not Sileo source addresses.

The server depends on `coreutils` and `dash`; Haku additionally needs
`uikittools`. Let Sileo resolve bootstrap dependencies from the existing
sources. If it cannot find the exact Haku server dependency, install the server
release file first rather than forcing Haku's dependency check.

## Verify and install from a terminal

Every release carries `build.json` with the package SHA-256 and source metadata.
The server package SHA-256 is:

```text
25c0844918bdedc0a3ddfd981bc55294cddf3e33562b63e618d3672ba5a1ec77
```

The matching Haku 0.2.1 client package SHA-256 is
`61d75cac40a54ff45f3cc3b47fb67dd6aed70a179956f1434b8d6eb4956aced7`.

On an already authenticated Mac, GitHub CLI can download the packages:

```sh
mkdir -p ~/Downloads/Haku
gh release download haku-v17.24.3-haku.1 --repo JackLee992/haku-server \
  --pattern '*.deb' --dir ~/Downloads/Haku
gh release download v0.2.1 --repo JackLee992/haku \
  --pattern '*.deb' --dir ~/Downloads/Haku
shasum -a 256 ~/Downloads/Haku/*.deb
```

Transfer them to the phone. For terminal installation, run as **root** on the
phone, substituting the actual file locations:

```sh
/var/jb/usr/bin/dpkg -i /var/mobile/Downloads/com.jacklee.haku-server_17.24.3+haku.1_iphoneos-arm64.deb
/var/jb/usr/bin/dpkg -i /var/mobile/Downloads/com.jacklee.haku_0.2.1_iphoneos-arm64.deb
/var/jb/usr/bin/hakuctl status
/var/jb/usr/sbin/haku-server --haku-info
```

Afterward run as **mobile**, the GUI user:

```sh
/var/jb/Applications/Haku.app/Haku --connection
/var/jb/Applications/Haku.app/Haku --list
```

The first command reads settings; the second proves a server connection. For
configuration, reset, SSH forwarding and connection failures, use
[PORTS.md](PORTS.md). For a bad `.deb`, redownload the release asset and compare
its SHA-256; a saved GitHub HTML page is not a Debian package.

## Application scope and upgrades

Haku 0.2.1 removes bundle-ID and fixed installation-directory filters. System,
rootless and user applications returned by haku-server are selectable. The
server must still be able to launch the target and the captured image must pass
identity and binary validation. Selecting an application restarts it.

Install upgrades through Sileo in server-first order when the dependency version
changes. The daemon's saved port and Haku's mobile-user destination survive
upgrades; verify both after installing. To uninstall the suite, remove Haku
first, then haku-server. The server package does not replace upstream Frida.

See [VALIDATION.md](VALIDATION.md) for measured capture, port, package and
coexistence results. A verified export is separate from signing, reinstalling
or testing the exported application's normal behavior.
