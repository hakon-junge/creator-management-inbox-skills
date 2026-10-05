"""Local state: the run log, the list of drafts this tool created, creator notes.

All of it lives under ~/.claude/inbox/ with owner-only permissions.
"""
import difflib
import hashlib
import json
import os
import re
import time

from . import body as body_mod, paths

CREATED = os.path.join(paths.RUNS, "created-drafts.json")
RATE_CARDS = os.path.join(paths.RUNS, "rate-cards.json")
KEEP_CARDS = 50


def fingerprint(text, rendered=False):
    """Of what a reader sees: draft HTML is rendered first, a rendered text as is."""
    t = text if rendered else body_mod.to_text(text)
    return hashlib.sha256(body_mod.normalize(t).encode()).hexdigest()[:16]


# --- drafts this tool created (only these may ever be deleted) --------------
def _load_created():
    try:
        with open(CREATED, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def remember_created(draft_id, thread_id, clean_html=None, run_log="learn"):
    """Remember the draft (only these may be deleted) and the CLEANED body it was
    saved with, until `inbox log` takes it: the text in learn mode, only its
    fingerprint in metadata mode, nothing when the run log is off."""
    d = _load_created()
    rec = {"thread_id": thread_id, "ts": time.time()}
    if clean_html is not None and run_log != "off":
        rec["fp"] = fingerprint(clean_html)
        if run_log == "learn":
            rec["body"] = clean_html
    d[draft_id] = rec
    paths.write_private(CREATED, json.dumps(d))


def created_by_us(draft_id):
    return draft_id in _load_created()


def saved_body(draft_id):
    """The cleaned body (or fingerprint) `inbox draft` saved for this draft."""
    rec = _load_created().get(draft_id or "", {})
    return {k: rec[k] for k in ("body", "fp") if k in rec}


def _release_body(draft_id):
    d = _load_created()
    if draft_id in d and ("body" in d[draft_id] or "fp" in d[draft_id]):
        d[draft_id].pop("body", None)
        d[draft_id].pop("fp", None)
        paths.write_private(CREATED, json.dumps(d))


def forget_created(draft_id):
    d = _load_created()
    d.pop(draft_id, None)
    paths.write_private(CREATED, json.dumps(d))


# --- rate cards `inbox rate` printed (their MAX must never reach a draft) ---
def _load_cards():
    try:
        with open(RATE_CARDS, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def record_card(card):
    """Keep the last 50 printed cards: format, private MAX, floor, timestamp, and the
    creator-facing numbers (OPEN, TARGET, ladder) of the same card."""
    cards = _load_cards()
    cards.append({"ts": time.time(), "format": card["format"], "max": card["max_private"],
                  "floor": card.get("floor"), "currency": card.get("currency"),
                  "public": sorted({card["open"], card["target"], *card.get("ladder", [])})})
    paths.write_private(RATE_CARDS, json.dumps(cards[-KEEP_CARDS:]))


def recent_cards(hours=24):
    cutoff = time.time() - hours * 3600
    return [c for c in _load_cards() if c.get("ts", 0) >= cutoff]


# --- run log -----------------------------------------------------------------
def log(entry, mode, keep_days):
    """Append one line per handled thread. mode: learn | metadata | off."""
    if mode == "off":
        return False
    entry = dict(entry)
    entry["ts"] = time.time()
    text = entry.pop("draft_text", None)
    saved = saved_body(entry.get("draft_id"))
    if saved:  # the cleaned body the draft was saved with beats the source file
        text = saved.get("body")
        entry["draft_fingerprint"] = saved["fp"]
        _release_body(entry["draft_id"])
    elif text is not None:
        entry["draft_fingerprint"] = fingerprint(text)
    if text is not None and mode == "learn":
        entry["draft_text"] = text
    paths.write_private(paths.RUN_LOG, json.dumps(entry) + "\n", mode="a")
    purge(keep_days)
    return True


def read_log(days):
    cutoff = time.time() - days * 86400
    out = []
    try:
        with open(paths.RUN_LOG, encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("ts", 0) >= cutoff:
                    out.append(e)
    except OSError:
        pass
    return out


def purge(keep_days):
    """Drop draft text older than keep_days; keep the metadata line."""
    cutoff = time.time() - keep_days * 86400
    d = _load_created()
    old = [k for k, v in d.items() if "body" in v and v.get("ts", 0) < cutoff]
    for k in old:
        d[k].pop("body")
    if old:
        paths.write_private(CREATED, json.dumps(d))
    if not os.path.exists(paths.RUN_LOG):
        return
    lines, changed = [], False
    with open(paths.RUN_LOG, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if "draft_text" in e and e.get("ts", 0) < cutoff:
                e.pop("draft_text")
                changed = True
            lines.append(json.dumps(e))
    if changed:
        paths.write_private(paths.RUN_LOG, "\n".join(lines) + "\n")


def compare(draft_html, sent_rendered):
    """zero_edit (exact match only) + similarity between the draft as saved and
    the sent message's rendered text (rendered_sent)."""
    a = body_mod.normalize(body_mod.to_text(draft_html))
    b = body_mod.normalize(sent_rendered)
    if not a or not b:
        return None
    return {"zero_edit": a == b,
            "similarity": round(difflib.SequenceMatcher(None, a, b).ratio(), 3)}


def rendered_sent(msg):
    """A sent message's own words: its HTML part rendered the way a draft is
    (signature and quoted history cut), else its plain text without the quote."""
    if msg.get("html"):
        return body_mod.to_text(body_mod.sent_body_html(msg["html"]))
    return _strip_quote(msg.get("body", "")).strip()


def _strip_quote(text):
    text = re.split(r"\n\s*On .{5,200}wrote:\s*\n", text or "", maxsplit=1)[0]
    text = re.split(r"\n-- \n", text, maxsplit=1)[0]
    return "\n".join(l for l in text.splitlines() if not l.startswith(">"))


# --- creator notes -----------------------------------------------------------
_FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def creators(query, folder=None):
    """Find creator notes in ~/.claude/inbox/creators/ by name, handle, email or
    promo code. Returns the front matter plus the file path - read the file for
    the rest."""
    q = query.lower().lstrip("@")
    folder = folder or paths.CREATORS
    hits = []
    if not os.path.isdir(folder):
        return hits
    for fn in sorted(os.listdir(folder)):
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        p = os.path.join(folder, fn)
        with open(p, encoding="utf-8") as f:
            text = f.read()
        fm = {}
        m = _FM.match(text)
        if m:
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
        haystack = " ".join([fn] + list(fm.values())).lower()
        if q in haystack:
            hits.append({"file": p, **fm})
    return hits
