#!/var/jb/usr/bin/sh
set -eu
PATH=/var/jb/usr/bin:/var/jb/usr/sbin:/usr/bin:/bin:/usr/sbin:/sbin
export PATH
. /var/jb/usr/libexec/haku-server-common.sh
HAKU_LABEL=system/com.jacklee.haku-server
case "${1:-}" in
    port)
        if [ "$#" = 1 ]; then haku_read_port; printf '%s\n' "$HAKU_PORT"; exit 0; fi
        if [ "$#" != 2 ] || ! haku_valid_port "$2"; then
            echo 'Usage: hakuctl port PORT (1-65535, excluding 27042/27043)' >&2; exit 2
        fi
        if [ "$(id -u)" != 0 ]; then echo 'Changing the server port requires root.' >&2; exit 1; fi
        HAKU_TEMP=$(mktemp /var/jb/etc/.haku-server.port.XXXXXX)
        trap 'rm -f "$HAKU_TEMP"' EXIT HUP INT TERM
        printf '%s\n' "$2" > "$HAKU_TEMP"
        chmod 644 "$HAKU_TEMP"
        mv -f "$HAKU_TEMP" /var/jb/etc/haku-server.port
        haku_launchctl kickstart -k "$HAKU_LABEL"
        printf 'haku-server configured for 127.0.0.1:%s. Set the same port in Haku > Connection.\n' "$2"
        ;;
    restart|stop)
        if [ "$(id -u)" != 0 ]; then echo 'Controlling the server requires root.' >&2; exit 1; fi
        if [ "$1" = restart ]; then haku_launchctl kickstart -k "$HAKU_LABEL";
        else haku_launchctl bootout "$HAKU_LABEL"; fi
        ;;
    start)
        if [ "$(id -u)" != 0 ]; then echo 'Starting the server requires root.' >&2; exit 1; fi
        haku_launchctl bootstrap system /var/jb/Library/LaunchDaemons/com.jacklee.haku-server.plist
        ;;
    status) haku_read_port; printf 'Endpoint: 127.0.0.1:%s\n' "$HAKU_PORT"; haku_launchctl print "$HAKU_LABEL" ;;
    *) echo 'Usage: hakuctl port [PORT] | status | restart | stop | start' >&2; exit 2 ;;
esac
