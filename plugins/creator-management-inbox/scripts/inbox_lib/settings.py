"""User settings, read from ~/.claude/inbox/profile/settings.md.

The file is Markdown so a non-technical user can read and edit it, but the
machine-readable part is a single fenced block:

    ```settings
    provider: gmail
    em_dashes: replace
    ```

Lines are `key: value`. `#` starts a comment. Unknown keys are ignored, missing
keys fall back to DEFAULTS, so an empty or missing file is always safe.
"""
import os
import re

from . import paths

DEFAULTS = {
    # Where drafts go: "gmail" (your real mailbox) or "demo" (sample emails,
    # drafts saved as local files - nothing touches a mailbox).
    "provider": "gmail",
    # Which demo `provider: demo` runs: "saas" (an app) or "ecommerce" (a
    # skincare brand). Ignored with provider: gmail.
    "demo_profile": "saas",
    # "replace" swaps every em dash or en dash for a spaced hyphen. "allow" leaves them.
    "em_dashes": "replace",
    # word=replacement pairs, comma separated. Replaced automatically in every draft.
    "banned_words": "",
    # "avoid" warns on any "!" in a draft; "allow" says nothing.
    "exclamation_marks": "allow",
    # Run log: "learn" keeps draft text for run_log_days so the workflow can
    # compare what you sent with what it drafted and improve. "metadata" keeps
    # only a fingerprint. "off" keeps nothing.
    "run_log": "learn",
    "run_log_days": "14",
    # Your own link domains (tracking links, shortener, website). Only links on
    # these domains are ever resolved over the network.
    "link_domains": "",
    # Teammate addresses that may be CC'd even if they are not on the thread.
    "team_addresses": "",
    # Upper bound on unread threads handled in one run.
    "max_threads": "50",
}

_BLOCK = re.compile(r"```settings\s*\n(.*?)```", re.S)
_LINE = re.compile(r"^\s*([a-z_]+)\s*:\s*(.*?)\s*$")


def _parse(text):
    m = _BLOCK.search(text)
    body = m.group(1) if m else text
    out = {}
    for raw in body.splitlines():
        line = raw.split("#", 1)[0]
        lm = _LINE.match(line)
        if lm:
            out[lm.group(1)] = lm.group(2)
    return out


def load():
    s = dict(DEFAULTS)
    try:
        with open(paths.SETTINGS, encoding="utf-8") as f:
            s.update({k: v for k, v in _parse(f.read()).items() if v != ""})
    except OSError:
        pass
    return s


def as_list(value):
    return [v.strip().lower() for v in (value or "").split(",") if v.strip()]


def banned_words(s):
    """{"honest": "straight", ...} from `banned_words: honest=straight, ...`."""
    pairs = {}
    for item in (s.get("banned_words") or "").split(","):
        if "=" in item:
            k, v = item.split("=", 1)
            if k.strip():
                pairs[k.strip()] = v.strip()
        elif item.strip():
            pairs[item.strip()] = ""
    return pairs


def exists():
    return os.path.exists(paths.SETTINGS)
