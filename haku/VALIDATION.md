# Validation

This file records haku-server checks independently from Haku's historical
upstream-server capture results. The supported packaging lane is rootless
`iphoneos-arm64`, `/var/jb`, deployment target iOS 15.0. Physical validation and
release hashes are added after execution; the deployment target alone is not a
compatibility claim.

The package installs and controls only `com.jacklee.haku-server`. Its default
listener is loopback `57042`; the package launcher always uses the configured
port. It does not modify the existing Frida package or its launchd service.

Host tests cover Debian archive ownership and parent directories, separate
payload/service names, preserved configuration, maintainer scripts and strict
port boundaries. Real-device checks must exercise enumeration, custom-port
reconnection, instrumentation and ordinary Frida coexistence before release.
