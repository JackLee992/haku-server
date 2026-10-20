#!/var/jb/usr/bin/sh
set -eu
. /var/jb/usr/libexec/haku-server-common.sh
haku_read_port
exec /var/jb/usr/sbin/haku-server --port "$HAKU_PORT"
