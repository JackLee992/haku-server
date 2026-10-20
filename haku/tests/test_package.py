from pathlib import Path
import importlib.util
import io
import json
import plistlib
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("haku_package", ROOT / "haku/package.py")
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


def read_deb(path):
    data = path.read_bytes()
    assert data[:8] == b"!<arch>\n"
    members, offset = {}, 8
    while offset < len(data):
        header = data[offset:offset + 60]
        assert header[58:] == b"`\n"
        name = header[:16].decode().strip().rstrip("/")
        size = int(header[48:58])
        members[name] = data[offset + 60:offset + 60 + size]
        offset += 60 + size + size % 2
    assert members["debian-binary"] == b"2.0\n"
    return members


class RootlessPackageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        binary = root / "server"
        binary.write_bytes(b"synthetic executable for archive tests")
        output = root / "server.deb"
        packager.package(binary, output, {"fixture": True})
        self.members = read_deb(output)

    def archive(self, name):
        return tarfile.open(fileobj=io.BytesIO(self.members[name]))

    def test_payload_is_separate_and_root_owned(self):
        with self.archive("data.tar.gz") as archive:
            seen = set()
            for entry in archive:
                path = Path(entry.name)
                self.assertTrue(entry.name == "./var" or entry.name.startswith("./var/"))
                self.assertNotIn("re.frida", entry.name)
                self.assertEqual((entry.uid, entry.gid), (0, 0))
                self.assertFalse(entry.mode & 0o022)
                if entry.isdir():
                    seen.add(path.as_posix())
                else:
                    self.assertIn(path.parent.as_posix(), seen)
            self.assertEqual(archive.getmember("./var/jb/usr/sbin/haku-server").mode, 0o755)
            self.assertEqual(archive.extractfile("./var/jb/etc/haku-server.port").read(), b"57042\n")
            self.assertEqual(json.load(archive.extractfile("./var/jb/usr/share/doc/haku-server/provenance.json")), {"fixture": True})

    def test_launchd_owns_only_haku_service(self):
        with self.archive("data.tar.gz") as archive:
            daemon = plistlib.load(archive.extractfile("./var/jb/Library/LaunchDaemons/com.jacklee.haku-server.plist"))
            self.assertEqual(daemon["Label"], "com.jacklee.haku-server")
            self.assertEqual(daemon["Program"], "/var/jb/usr/bin/sh")
            self.assertEqual(daemon["ProgramArguments"], ["/var/jb/usr/bin/sh", "/var/jb/usr/libexec/haku-server-launcher"])
            self.assertEqual(daemon["UserName"], "root")
            self.assertTrue(daemon["RunAtLoad"])
            self.assertTrue(daemon["KeepAlive"])

    def test_control_preserves_config_and_does_not_replace_frida(self):
        with self.archive("control.tar.gz") as archive:
            control = archive.extractfile("./control").read().decode()
            self.assertIn("Package: com.jacklee.haku-server\n", control)
            self.assertIn("Architecture: iphoneos-arm64\n", control)
            for forbidden in ("Conflicts:", "Replaces:", "Provides:", "re.frida.server"):
                self.assertNotIn(forbidden, control)
            self.assertEqual(archive.extractfile("./conffiles").read(), b"/var/jb/etc/haku-server.port\n")
            for name in ("postinst", "prerm"):
                script = archive.extractfile("./" + name).read()
                self.assertTrue(script.startswith(b"#!/var/jb/usr/bin/sh\n"))
                self.assertNotIn(b"re.frida.server", script)
                subprocess.run(["sh", "-n"], input=script, check=True)


class ShellPortTests(unittest.TestCase):
    def check_port(self, port):
        return subprocess.run(["sh", "-c", '. "$1"; haku_valid_port "$2"', "test", str(ROOT / "haku/packaging/common.sh"), port], capture_output=True).returncode

    def test_custom_ports_and_bounds(self):
        for port in ("1", "57042", "58000", "65535", "00001"):
            with self.subTest(port=port):
                self.assertEqual(self.check_port(port), 0)

    def test_invalid_and_frida_ports(self):
        for port in ("", "0", "65536", "-1", "+57", "57.0", "57042 ", " 57042", "５７０４２", "27042", "27043", "000001", "1;echo wrong"):
            with self.subTest(port=port):
                self.assertNotEqual(self.check_port(port), 0)

    def test_packaging_scripts_parse(self):
        for path in (ROOT / "haku/packaging").glob("*.sh"):
            subprocess.run(["sh", "-n", str(path)], check=True)
