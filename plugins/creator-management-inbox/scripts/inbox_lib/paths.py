"""Where everything lives on the user's machine.

One home directory holds everything that belongs to the USER rather than to the
plugin: the mailbox token, the profile (voice, company facts, settings), creator
notes, the run log and demo output. It sits outside the plugin cache on purpose,
so a plugin update never touches it and an uninstall never deletes it.

Override the location with $INBOX_HOME (useful for tests).
"""
import os
import stat

HOME = os.path.expanduser(os.environ.get("INBOX_HOME") or "~/.claude/inbox")

TOKEN = os.path.join(HOME, "token.json")
CLIENT_SECRET = os.path.join(HOME, "client_secret.json")
VENV = os.path.join(HOME, "venv")
PROFILE = os.path.join(HOME, "profile")
CREATORS = os.path.join(HOME, "creators")
ATTACHMENTS = os.path.join(HOME, "attachments")
RUNS = os.path.join(HOME, "runs")
RUN_LOG = os.path.join(RUNS, "runs.jsonl")
RUN_MARKER = os.path.join(HOME, ".run-active")
DEMO_OUT = os.path.join(HOME, "demo-output")
SETTINGS = os.path.join(PROFILE, "settings.md")
SIGNATURE = os.path.join(PROFILE, "signature.html")

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
DEMO_ROOT = os.path.join(PLUGIN_ROOT, "demo")
DEMO_INBOX = os.path.join(DEMO_ROOT, "inbox")
PROFILE_TEMPLATES = os.path.join(PLUGIN_ROOT, "skills", "company-context",
                                 "templates")


def demo_names():
    """The demos that ship: `saas` (demo/inbox + demo/profile) and every
    demo/inbox-<name> that has a matching demo/profile-<name>."""
    names = {"saas"}
    if os.path.isdir(DEMO_ROOT):
        for fn in os.listdir(DEMO_ROOT):
            if fn.startswith("inbox-") and os.path.isdir(
                    os.path.join(DEMO_ROOT, "profile-" + fn[len("inbox-"):])):
                names.add(fn[len("inbox-"):])
    return sorted(names)


def demo_dirs(name=None):
    """(inbox folder, profile folder) for the `demo_profile` setting. `saas` (the
    default) keeps its original folders; any other demo lives in
    demo/inbox-<name> and demo/profile-<name>. Unknown name -> ValueError."""
    name = (name or "saas").strip().lower()
    if name not in demo_names():
        raise ValueError(f"unknown demo_profile '{name}' in settings.md (use "
                         + " or ".join(demo_names()) + ")")
    if name == "saas":
        return DEMO_INBOX, os.path.join(DEMO_ROOT, "profile")
    return (os.path.join(DEMO_ROOT, "inbox-" + name),
            os.path.join(DEMO_ROOT, "profile-" + name))


def ensure_private_dir(path):
    """Create a directory readable only by the owner (0700), and tighten it if
    it already exists with looser permissions."""
    os.makedirs(path, mode=0o700, exist_ok=True)
    mode = stat.S_IMODE(os.stat(path).st_mode)
    if mode & 0o077:
        os.chmod(path, 0o700)
    return path


def write_private(path, data, mode="w"):
    """Write a file that only the owner can read (0600). The file is created
    with the restrictive mode from the start - never written world-readable and
    tightened afterwards."""
    ensure_private_dir(os.path.dirname(path))
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if "a" in mode:
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    fd = os.open(path, flags, 0o600)
    os.chmod(path, 0o600)
    with os.fdopen(fd, mode) as f:
        f.write(data)
