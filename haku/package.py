#!/usr/bin/env python3
"""Create a standalone rootless Debian package from the source-built server."""
from pathlib import Path
import argparse
import gzip
import hashlib
import io
import json
import plistlib
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[1]
IDENTITY=json.loads((ROOT/"haku/upstream.json").read_text())


def compressed_tar(entries):
    out=io.BytesIO()
    with tarfile.open(fileobj=out,mode="w",format=tarfile.GNU_FORMAT) as archive:
        for name,data,mode in entries:
            member=tarfile.TarInfo(name)
            member.uid=member.gid=member.mtime=0
            member.mode=mode
            if data is None: member.type=tarfile.DIRTYPE
            else: member.size=len(data)
            archive.addfile(member,io.BytesIO(data) if data is not None else None)
    return gzip.compress(out.getvalue(),mtime=0)


def package(binary,destination,provenance=None):
    version=IDENTITY["haku_server_version"]
    control=f"""Package: com.jacklee.haku-server
Name: haku-server
Version: {version}
Architecture: iphoneos-arm64
Section: Development
Maintainer: JackLee992
Author: Frida contributors, JackLee992
Description: Haku's source-built Frida server fork with independent port configuration
Depends: firmware (>= 15.0), coreutils, dash
Homepage: https://github.com/JackLee992/haku-server
"""
    postinst="""#!/var/jb/usr/bin/sh
set -eu
. /var/jb/usr/libexec/haku-server-common.sh
if [ "$1" = configure ]; then
    haku_launchctl bootout system/com.jacklee.haku-server >/dev/null 2>&1 || true
    haku_launchctl bootstrap system /var/jb/Library/LaunchDaemons/com.jacklee.haku-server.plist
fi
"""
    prerm="""#!/var/jb/usr/bin/sh
. /var/jb/usr/libexec/haku-server-common.sh
case "$1" in remove|upgrade|deconfigure) haku_launchctl bootout system/com.jacklee.haku-server >/dev/null 2>&1 || true ;; esac
"""
    control_tar=compressed_tar([("./control",control.encode(),0o644),("./postinst",postinst.encode(),0o755),("./prerm",prerm.encode(),0o755),("./conffiles",b"/var/jb/etc/haku-server.port\n",0o644)])
    daemon={"Label":"com.jacklee.haku-server","Program":"/var/jb/usr/bin/sh","ProgramArguments":["/var/jb/usr/bin/sh","/var/jb/usr/libexec/haku-server-launcher"],"UserName":"root","RunAtLoad":True,"KeepAlive":True,"ThrottleInterval":10,"StandardOutPath":"/var/jb/var/log/haku-server.log","StandardErrorPath":"/var/jb/var/log/haku-server.log"}
    payload={
        "usr/sbin/haku-server":(binary.read_bytes(),0o755),
        "usr/bin/hakuctl":((ROOT/"haku/packaging/hakuctl.sh").read_bytes(),0o755),
        "usr/libexec/haku-server-launcher":((ROOT/"haku/packaging/launcher.sh").read_bytes(),0o755),
        "usr/libexec/haku-server-common.sh":((ROOT/"haku/packaging/common.sh").read_bytes(),0o644),
        "etc/haku-server.port":(b"57042\n",0o644),
        "Library/LaunchDaemons/com.jacklee.haku-server.plist":(plistlib.dumps(daemon),0o644),
        "usr/share/doc/haku-server/COPYING":((ROOT/"COPYING").read_bytes(),0o644),
        "usr/share/doc/haku-server/provenance.json":(json.dumps(provenance or IDENTITY,indent=2).encode()+b"\n",0o644),
    }
    directories={"./var","./var/jb","./var/jb/var","./var/jb/var/log"}
    for name in payload:
        for parent in (Path("./var/jb")/name).parents:
            if str(parent)!=".":directories.add("./"+parent.as_posix())
    entries=[(name+"/",None,0o755) for name in sorted(directories,key=lambda n:(n.count("/"),n))]
    entries.extend(("./var/jb/"+name,data,mode) for name,(data,mode) in sorted(payload.items()))
    data_tar=compressed_tar(entries)
    with destination.open("wb") as out:
        out.write(b"!<arch>\n")
        for name,data in [("debian-binary",b"2.0\n"),("control.tar.gz",control_tar),("data.tar.gz",data_tar)]:
            header=f"{name+'/':<16}{0:<12}{0:<6}{0:<6}{'100644':<8}{len(data):<10}`\n".encode()
            assert len(header)==60
            out.write(header);out.write(data)
            if len(data)%2:out.write(b"\n")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--binary",type=Path,default=ROOT/"build/server/haku-server")
    a=p.parse_args()
    revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    paths=subprocess.check_output(["git","ls-files","-c","-o","--exclude-standard","-z"],cwd=ROOT).split(b"\0")
    digest=hashlib.sha256()
    for name in sorted(set(paths)-{b""}):
        path=ROOT/name.decode()
        if path.is_file():
            digest.update(name+b"\0"+path.read_bytes()+b"\0")
    submodules=subprocess.check_output(["git","submodule","status","--recursive"],cwd=ROOT,text=True).strip().splitlines()
    gum_revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT/"subprojects/frida-gum",text=True).strip()
    dirty=bool(subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).strip())
    metadata=dict(IDENTITY,source_revision=revision,source_sha256=digest.hexdigest(),source_dirty=dirty,submodules=submodules,gum_revision=gum_revision,binary_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),build_type="compiled from source",architecture="ios-arm64",minimum_ios="15.0",compat="native",payload_architectures=["arm64","arm64e"])
    dist=ROOT/"dist";dist.mkdir(exist_ok=True)
    target=dist/f"com.jacklee.haku-server_{IDENTITY['haku_server_version']}_iphoneos-arm64.deb"
    package(a.binary,target,metadata)
    metadata.update(package=target.name,package_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (dist/"build.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps(metadata,indent=2))


if __name__=="__main__":main()
