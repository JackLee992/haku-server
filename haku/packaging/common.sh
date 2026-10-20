# Shared data validation and launchctl lookup for the rootless package.
haku_valid_port() {
    case "$1" in ''|*[!0-9]*) return 1 ;; esac
    [ "${#1}" -le 5 ] && [ "$1" -ge 1 ] && [ "$1" -le 65535 ] && [ "$1" -ne 27042 ] && [ "$1" -ne 27043 ]
}
haku_read_port() {
    HAKU_PORT=57042
    if [ -f /var/jb/etc/haku-server.port ]; then
        IFS= read -r HAKU_PORT < /var/jb/etc/haku-server.port || [ -n "$HAKU_PORT" ]
    fi
    if ! haku_valid_port "$HAKU_PORT"; then
        echo 'Invalid haku-server port configuration; expected 1-65535 excluding 27042/27043.' >&2
        return 1
    fi
}
haku_launchctl() {
    for HAKU_LAUNCHCTL in /var/jb/bin/launchctl /var/jb/usr/bin/launchctl /bin/launchctl /usr/bin/launchctl; do
        if [ -x "$HAKU_LAUNCHCTL" ]; then "$HAKU_LAUNCHCTL" "$@"; return "$?"; fi
    done
    echo 'launchctl is unavailable.' >&2
    return 127
}
haku_restart() {
    haku_launchctl bootout system/com.jacklee.haku-server >/dev/null 2>&1 || true
    haku_launchctl bootstrap system /var/jb/Library/LaunchDaemons/com.jacklee.haku-server.plist
}
