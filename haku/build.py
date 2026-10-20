#!/usr/bin/env python3
"""Build haku-server from the maintained source fork, then package for Sileo."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    if sys.version_info<(3,10):raise SystemExit("Python 3.10+ is required")
    env=os.environ.copy();env.update(PYTHON=sys.executable,IOS_CERTID="-",MACOS_CERTID="-")
    flags=["--host=ios-arm64","--prefix=/usr","--with-apple-min-os=ios=15.0","--with-frida-version=17.24.3","--enable-server","--disable-gadget","--disable-portal","--disable-inject","--disable-tests","--disable-compiler-backend","--disable-fruity-backend","--disable-droidy-backend","--disable-simmy-backend","--disable-barebone-backend","--with-assets=embedded","--with-compat=native"]
    if not (ROOT/"build/build.ninja").exists():
        subprocess.run([str(ROOT/"configure"),*flags],cwd=ROOT,env=env,check=True)
    else:
        subprocess.run([sys.executable,str(ROOT/"releng/meson/meson.py"),"configure",str(ROOT/"build"),"-Dcompat=native"],cwd=ROOT,env=env,check=True)
    subprocess.run(["make",f"-j{min(os.cpu_count() or 4,8)}","haku-server"],cwd=ROOT,env=env,check=True)
    ldid=os.environ.get("LDID") or shutil.which("ldid")
    if not ldid:raise SystemExit("Set LDID to an ldid executable, or install ldid with Homebrew")
    subprocess.run([ldid,"-S"+str(ROOT/"server/haku-server.xcent"),str(ROOT/"build/server/haku-server")],check=True)
    subprocess.run([sys.executable,str(ROOT/"haku/package.py")],cwd=ROOT,check=True)


if __name__=="__main__":main()
