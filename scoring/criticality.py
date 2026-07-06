"""Détection des process protégés — jamais candidats à un kill préventif."""

PROTECTED_NAMES = {
    "systemd",
    "systemd-logind",
    "systemd-journald",
    "systemd-udevd",
    "dbus-daemon",
    "dbus-broker",
    "sshd",
    "NetworkManager",
    "Xorg",
    "sway",
    "kwin_wayland",
    "gnome-shell",
    "plasmashell",
    "smart-oomd",
}

OOM_SCORE_ADJ_NEVER_KILL = -1000


def is_protected(pid: int, name: str, oom_score_adj: int, own_pid: int) -> bool:
    if pid == 1 or pid == own_pid:
        return True
    if oom_score_adj <= OOM_SCORE_ADJ_NEVER_KILL:
        return True
    return name in PROTECTED_NAMES
