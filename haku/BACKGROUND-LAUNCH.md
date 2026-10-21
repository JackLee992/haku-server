# Background capture launches

Haku 0.2.2 requires haku-server 17.24.3+haku.2 and sends the boolean spawn
auxiliary option `haku-background=true`. The target's main thread is still
suspended for acquisition; the target is launched without becoming the visible
application. This keeps the Haku progress UI in the foreground.

The FBS launcher uses `FBSOpenApplicationOptionKeyActivateSuspended`, also used
by [LLVM debugserver](https://github.com/llvm/llvm-project/blob/main/lldb/tools/debugserver/source/MacOSX/MachProcess.mm).
The legacy SBS branch uses its existing suspended-launch parameter. A missing
FBS constant produces an explicit unsupported error. Non-boolean option values
are rejected. The tvOS-specific launcher does not support this option.

Omitting the option, or sending false, preserves the upstream launch behavior.
The option travels through the existing Frida 17.24.3 auxiliary dictionary;
the wire protocol is unchanged. An older server can ignore unknown options,
so the client package pins the matching server version rather than assuming
that protocol compatibility establishes support for background capture.

The phone UI regression checks that Haku stays active through selection,
native capture and packaging. A foreground-only CLI test cannot prove this
lifecycle property. Haku also requests finite background time for brief user
interruptions and cancels if that time expires.
