#!/usr/bin/env python3
"""Send guard for creator-management-inbox. Runs before Claude's file, shell, web
and MCP tools (hooks.json).

Always:
  - blocks reading, writing or copying your Gmail token or OAuth client file, in
    any spelling (~, $HOME, $INBOX_HOME, //, globs like tok*, `cd` into the
    folder and a relative name); only the `inbox` tool reads them, itself
  - blocks Gmail / Graph / SMTP send calls in a shell command or a written file
  - blocks a mail connector's (gmail, outlook, mail, email or inbox in the tool
    name) send, reply, forward, trash, delete, modify, label, move and draft
    tools: drafts go through `inbox draft`, with its checks

While an inbox run is active (`inbox run start` ... `inbox run end`):
  - blocks every MCP tool that acts (send, reply, create, update, delete, post,
    share, ... - reads stay allowed), and WebFetch
  - blocks a mail tool's trash, spam, archive and label-removing actions whatever the
    connector is called, and shell network clients (curl, wget, nc, ...)
  - blocks changing profile/settings.md and profile/me.md: they hold who may receive
    a draft and the sign-off limit, so an email can't talk its way past those checks
  - blocks removing the run marker; only `inbox run end` clears it

It is a deny-list. It stops accidents and plain attempts; a command written to hide
what it does (a path or a call assembled from pieces) can get past it.

It fails OPEN on its own errors (a broken guard must not break Claude Code),
and it is one layer of several - see SECURITY.md.
"""
import fnmatch
import json
import os
import re
import sys
import time

USER_HOME = os.path.expanduser("~")
HOME = os.path.normpath(os.path.expanduser(os.environ.get("INBOX_HOME") or "~/.claude/inbox"))
HOMES = {HOME, os.path.normpath(os.path.join(USER_HOME, ".claude", "inbox"))}
HOMES |= {os.path.realpath(h) for h in HOMES}
MARKER = os.path.join(HOME, ".run-active")
RUN_TTL = 6 * 3600
SECRETS = ("token.json", "client_secret.json")
SECRET_GLOBS = ("token.json", "client_secret*.json")

SEND_CALL = re.compile(
    r"(gmail/v1/users/[^/\s]+/(messages|drafts)/send"
    r"|\b(messages|drafts)\(\)\s*\.\s*send\s*\("
    r"|graph\.microsoft\.com/[^\s]*/(sendMail|send)\b"
    r"|smtplib|sendmail\b)", re.I)
LOCAL_SEND = re.compile(r"osascript\b[^\n]*\bMail\b[^\n]*\bsend\b|\b(msmtp|swaks|mutt)\b"
                        r"|\bmail\s+-s\b", re.I)
NET_CLIENT = re.compile(r"(?:^|[\s;|&(`])(curl|wget|nc|ncat|netcat|sftp|ftp)\s")
MAIL_CONNECTOR = re.compile(r"gmail|outlook|mail|email|inbox", re.I)
MAIL_ACTIONS = {"send", "reply", "forward", "trash", "untrash", "delete", "modify", "label",
                "unlabel", "move", "archive", "spam", "mark", "unmark"}
# During a run these stop a tool whatever its connector is called (a connector can
# carry an id for a name). mark / unmark alone are too common outside mail.
RUN_MAIL_ACTIONS = MAIL_ACTIONS - {"mark", "unmark"}
ACT_VERBS = {"send", "reply", "forward", "create", "update", "delete", "post", "share",
             "schedule", "upload", "move", "label", "invite", "publish", "write", "set", "add",
             "remove"}
READ_VERBS = {"get", "list", "search", "read", "fetch", "find", "query", "view", "show",
              "count", "describe", "lookup", "download", "export", "check", "resolve"}
HOME_WORDS = re.compile(r"\.claude/inbox|INBOX_HOME", re.I)
SECRET_WORDS = re.compile(r"tok|client_secret|secret|refresh", re.I)
COPY_ALL = re.compile(r"\b(cp|rsync|scp|tar|zip|7z|ditto|rclone)\b|\b(grep|rg|ag|egrep)\b"
                      r"[^|;&]*\s-\w*[rR]|\bfind\b[^|;&]*-exec|\bcat\b[^|;&]*\*")
DELETE = re.compile(r"\b(rm|unlink|rmdir|shred|srm|mv|truncate|trash|touch|del)\b|-delete\b"
                    r"|\.unlink\(|os\.remove|shutil\.(rmtree|move)|Remove-Item", re.I)
RUN_CMD = re.compile(r"^\s*(?:\S*/)?inbox\s+run\s+(?:start|end)\s*$")
LOCKED_PROFILE = ("settings.md", "me.md")
# Quotes are already stripped (paths_in): open(p, "w") arrives as open(p, w).
IN_PLACE = re.compile(r"\b(sed|perl|ruby)\b[^|;&]*\s-\w*i|open\([^)]*,\s*(mode\s*=\s*)?[wax]"
                      r"|\.write(_text|_bytes)?\(|\bof=\S*(settings|me)\.md\b", re.I)
COPY_TO = re.compile(r"\b(cp|mv|ln|install|rsync|ditto|scp)\b")   # change their destination
REDIRECT = re.compile(r"(?:>>?|\btee\b(?:\s+-\w+)*)\s*([^\s;|&<>()]+)")
DOC_EXT = (".md", ".markdown", ".rst", ".html", ".htm", ".csv", ".json")


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "creator-management-inbox guard: " + reason}}))
    sys.exit(0)


def run_active():
    try:
        return time.time() - os.path.getmtime(MARKER) < RUN_TTL
    except OSError:
        return False


# --- paths in any spelling ------------------------------------------------------
def _braces(p):
    m = re.search(r"\{([^{}]*,[^{}]*)\}", p)
    if not m:
        return [p]
    return [x for alt in m.group(1).split(",")
            for x in _braces(p[:m.start()] + alt + p[m.end():])]


def expand(tok, cwd=None):
    t = tok
    for var in ("${INBOX_HOME}", "$INBOX_HOME"):
        t = t.replace(var, HOME)
    for var in ("${HOME}", "$HOME"):
        t = t.replace(var, USER_HOME)
    if t.startswith("~"):
        t = os.path.expanduser(t)
    t = re.sub(r"/{2,}", "/", t)
    if not t.startswith("/"):
        if not cwd:
            return None
        t = os.path.join(cwd, t)
    return os.path.normpath(t)


def _is_home(d):
    return os.path.normpath(d) in HOMES or os.path.realpath(d) in HOMES


def secret_path(path):
    """An absolute path, maybe a glob, that names the token or the client file."""
    for p in _braces(path):
        d, b = os.path.split(p)
        if _is_home(d) and (any(fnmatch.fnmatchcase(s, b) for s in SECRETS)
                            or any(fnmatch.fnmatchcase(b, g) for g in SECRET_GLOBS)
                            or "$" in b):   # a loop variable for a name reads every file
            return True
        if any(c in d for c in "*?[") and any(
                fnmatch.fnmatchcase(os.path.join(h, s), p) for h in HOMES for s in SECRETS):
            return True
    return False


def locked_profile(path):
    """profile/settings.md or profile/me.md of the inbox folder."""
    d, b = os.path.split(path)
    return (b in LOCKED_PROFILE and os.path.basename(d) == "profile"
            and _is_home(os.path.dirname(d)))


def copy_lands_on_profile(found):
    """The last path (a copy's destination) is a locked file, or the profile folder
    with a source of the same name."""
    last = found[-1].rstrip(os.sep)
    if locked_profile(last):
        return True
    return (os.path.basename(last) == "profile" and _is_home(os.path.dirname(last))
            and any(os.path.basename(p) in LOCKED_PROFILE for p in found[:-1]))


def changes_profile(text, cwd=None):
    """A command that rewrites a locked profile file (reading it stays allowed)."""
    found, flat = paths_in(text, cwd)
    if found and COPY_TO.search(flat) and copy_lands_on_profile(found):
        return True
    if not any(locked_profile(p) for p in found):
        return False
    targets = [os.path.basename(t) for t in REDIRECT.findall(flat)]
    return bool(IN_PLACE.search(flat) or DELETE.search(flat)
                or any(t in LOCKED_PROFILE for t in targets))


def marker_path(path):
    d, b = os.path.split(path)
    return _is_home(d) and fnmatch.fnmatchcase(".run-active", b)


def home_or_above(path, skip_hidden=False):
    """The inbox folder itself or a folder above it. skip_hidden: a search that
    skips hidden folders (ripgrep) never reaches it through .claude."""
    for h in HOMES:
        if path == h:
            return True
        if h.startswith(path.rstrip("/") + "/"):
            rest = h[len(path.rstrip("/")) + 1:]
            if not (skip_hidden and any(c.startswith(".") for c in rest.split("/"))):
                return True
    return False


def paths_in(text, cwd=None):
    """Every path-like token of a command or a script, expanded, following `cd`.
    Quotes and backslashes are dropped so they can't split a path."""
    flat = re.sub(r"[\"'\\]", "", text)
    tokens = [t for t in re.split(r"[\s;|&<>()`=,+]+", flat) if t]
    out, cur, prev = [], cwd, ""
    for tok in tokens:
        p = expand(tok, cur)
        if prev in ("cd", "pushd") and p:
            cur = p
        elif p and tok != os.sep:   # a lone slash is text ("a or b") far more often than a path
            out.append(p)
        prev = tok
    return out, flat


def secret_text(text, cwd=None, words=True):
    """The text reaches the token or the client file. words: also when it names
    the inbox folder and a secret-sounding word (a path built from pieces)."""
    found, flat = paths_in(text, cwd)
    if any(secret_path(p) for p in found):
        return True
    if any(home_or_above(p) for p in found) and COPY_ALL.search(flat):
        return True
    named = HOME_WORDS.search(flat) or any(h in flat for h in HOMES)
    return bool(words and named and SECRET_WORDS.search(flat))


def removes_marker(text, cwd=None):
    if RUN_CMD.match(text) or not DELETE.search(text):
        return False
    found, flat = paths_in(text, cwd)
    return "run-active" in flat or any(marker_path(p) or home_or_above(p) for p in found)


# --- MCP tool names --------------------------------------------------------------
def action_words(tool):
    action = tool.split("__")[-1]
    words = [w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", action)]
    return action.lower(), words + [w[:-1] for w in words if w.endswith("s") and len(w) > 3]


def is_read(words):
    """The tool's first verb reads (gmail_list_labels, get_message): allowed."""
    verb = next((w for w in words if w in READ_VERBS | ACT_VERBS | MAIL_ACTIONS), None)
    return verb in READ_VERBS


def main():
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    cwd = data.get("cwd")
    active = run_active()
    secret = ("the Gmail token and OAuth client file are only read by the `inbox` "
              "tool. Do not read, copy, print or change them.")

    locked = ("settings.md and me.md hold who may receive a draft and your sign-off "
              "limit, so they are not changed during an inbox run. Propose the change "
              "in the report and make it after `inbox run end`.")

    if tool == "Bash":
        cmd = ti.get("command", "")
        if secret_text(cmd, cwd):
            deny(secret)
        if SEND_CALL.search(cmd) or LOCAL_SEND.search(cmd):
            deny("sending email is not part of this workflow. Create a draft "
                 "with `inbox draft`; a human sends it.")
        if active and removes_marker(cmd, cwd):
            deny("the run marker is cleared only by `inbox run end`.")
        if active and changes_profile(cmd, cwd):
            deny(locked)
        if active and NET_CLIENT.search(cmd):
            deny("no network commands during an inbox run: nothing an email says is "
                 "fetched or posted. `inbox resolve` follows your own link_domains; "
                 "anything else waits for `inbox run end`.")
        return

    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        target = ti.get("file_path") or ti.get("notebook_path") or ""
        p = expand(target, cwd)
        if p and secret_path(p):
            deny(secret)
        content = "\n".join(str(x) for x in (
            [ti.get("content"), ti.get("new_string"), ti.get("new_source")]
            + [e.get("new_string") for e in ti.get("edits") or [] if isinstance(e, dict)])
            if x)
        if secret_text(content, words=not target.lower().endswith(DOC_EXT)):
            deny(secret + " (this file would reach them)")
        if SEND_CALL.search(content):
            deny("a file that sends email is not part of this workflow; drafts go "
                 "through `inbox draft`.")
        if active and (p and marker_path(p) or removes_marker(content)):
            deny("the run marker is cleared only by `inbox run end`.")
        if active and p and locked_profile(p):
            deny(locked)
        return

    if tool in ("Read", "Grep", "Glob"):
        for key in ("file_path", "path") + (("pattern",) if tool == "Glob" else ()):
            v = ti.get(key)
            if not v:
                continue
            base = ti.get("path") if key == "pattern" and tool == "Glob" else None
            p = expand(v, expand(base, cwd) if base else cwd)
            if p and secret_path(p):
                deny("the Gmail token and OAuth client file are off limits.")
        if tool == "Grep":
            p = expand(ti.get("path") or ".", cwd)
            glob = ti.get("glob")
            if p and home_or_above(p, skip_hidden=True) and (
                    not glob or any(fnmatch.fnmatchcase(s, g) for s in SECRETS
                                    for g in _braces(glob))):
                deny("searching the inbox folder would read the Gmail token - search "
                     "profile/ or creators/ instead.")
        return

    if tool == "WebFetch" and active:
        deny("no web fetches during an inbox run: links in emails are never fetched; "
             "`inbox resolve` follows your own link_domains.")

    if tool.startswith("mcp__"):
        action, words = action_words(tool)
        mail = MAIL_CONNECTOR.search(tool)
        if mail and not is_read(words) and (
                MAIL_ACTIONS & set(words) or "create_draft" in action or "update_draft" in action
                or "createdraft" in action or "updatedraft" in action):
            deny(f"'{action}' on a mail connector is blocked: drafts go through "
                 "`inbox draft` (with its checks) and a human sends them.")
        if active and not is_read(words) and (ACT_VERBS | RUN_MAIL_ACTIONS) & set(words):
            deny(f"'{action}' is blocked during an inbox run - the run only reads and "
                 "creates drafts through `inbox draft`.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
