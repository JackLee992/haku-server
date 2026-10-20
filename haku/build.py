#!/usr/bin/env python3
"""Compile arm64/arm64e Haku servers, sign the universal executable and package it."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMON_FLAGS = [
    "--prefix=/usr", "--with-apple-min-os=ios=15.0",
    "--with-frida-version=17.24.3", "--enable-server", "--disable-gadget",
    "--disable-portal", "--disable-inject", "--disable-tests",
    "--disable-compiler-backend", "--disable-fruity-backend",
    "--disable-droidy-backend", "--disable-simmy-backend",
    "--disable-barebone-backend", "--with-assets=embedded",
]


def compile_server(build, arch, flags, options):
    env = os.environ.copy()
    env.update(PYTHON=sys.executable, IOS_CERTID="-", MACOS_CERTID="-",
               MESON_BUILD_ROOT=str(build))
    meson = str(ROOT / "releng/meson/meson.py")
    if not (build / "build.ninja").exists():
        subprocess.run([str(ROOT / "configure"), f"--host=ios-{arch}",
                        *COMMON_FLAGS, *flags], cwd=ROOT, env=env, check=True)
    else:
        subprocess.run([sys.executable, meson, "configure", str(build), *options],
                       cwd=ROOT, env=env, check=True)
    subprocess.run([sys.executable, meson, "compile", "-C", str(build),
                    "-j", str(min(os.cpu_count() or 4, 8)), "haku-server"],
                   cwd=ROOT, env=env, check=True)
    return build / "server/haku-server"


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ is required")
    primary = ROOT / "build"
    basic = compile_server(primary, "arm64", ["--with-compat=native"], ["-Dcompat=native"])
    # The arm64e server executes on PAC devices. An arm64-only server cannot
    # create every thread state needed during arm64e system-assisted app startup.
    # Embed the already-built legacy payloads, avoiding a recursive compat build.
    legacy_helper = str(primary / "src/frida-helper")
    legacy_agent = str(primary / "lib/agent/frida-agent.dylib")
    modern = compile_server(
        ROOT / ".haku-build/arm64e", "arm64e",
        ["--with-compat=disabled", f"--with-helper-legacy={legacy_helper}",
         f"--with-agent-legacy={legacy_agent}"],
        ["-Dcompat=disabled", f"-Dhelper_legacy={legacy_helper}",
         f"-Dagent_legacy={legacy_agent}"],
    )
    universal = primary / "haku-server"
    subprocess.run(["xcrun", "lipo", "-create", str(basic), str(modern),
                    "-output", str(universal)], check=True)
    subprocess.run(["codesign", "--force", "--sign", "-", "--identifier",
                    "com.jacklee.haku-server", "--entitlements",
                    str(ROOT / "server/haku-server.xcent"), str(universal)], check=True)
    subprocess.run(["codesign", "--verify", "--strict", "--all-architectures",
                    str(universal)], check=True)
    subprocess.run([sys.executable, str(ROOT / "haku/package.py"),
                    "--binary", str(universal)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
