"""Demo mailbox: fictional creator emails, drafts saved as local files.

Lets anyone watch the whole workflow run in minutes, before connecting a real
mailbox and without any account, token or network. Every creator, brand and
number in demo/ is made up. `demo_profile` in settings picks the demo: `saas`
(demo/inbox + demo/profile) or another one (demo/inbox-<name> + demo/profile-<name>).

Drafts land in ~/.claude/inbox/demo-output/, with an index.html you can open in
a browser to read each draft under the email it answers.
"""
import html as h_lib
import json
import os
import re
import time
from email.utils import getaddresses

from . import paths

DEMO_ADDRESS = "you@yourbrand.example"


class Demo:
    name = "demo"

    def __init__(self, demo_profile=None):
        inbox_dir, self.profile_dir = paths.demo_dirs(demo_profile)
        self.threads = {}
        for fn in sorted(os.listdir(inbox_dir)):
            if fn.endswith(".json"):
                with open(os.path.join(inbox_dir, fn), encoding="utf-8") as f:
                    t = json.load(f)
                self.threads[t["thread_id"]] = t
        try:
            with open(os.path.join(self.profile_dir, "me.md"), encoding="utf-8") as f:
                m = re.search(r"`\{\{OPERATOR_EMAIL\}\}`:\s*(\S+@\S+)", f.read())
        except OSError:
            m = None
        self.address = m.group(1).lower() if m else DEMO_ADDRESS
        paths.ensure_private_dir(paths.DEMO_OUT)

    def whoami(self):
        return self.address

    def reply_from(self, thread):
        return self.address

    def signature(self, sender=None):
        try:
            with open(os.path.join(self.profile_dir, "signature.html"), encoding="utf-8") as f:
                return f.read().strip()
        except OSError:
            return ('<div style="color:#555"><b>Sam Rivera</b> | Creator Partnerships Lead, '
                    'Fernwell (fictional)</div>')

    def participants(self, thread):
        return participants(thread, self.address)

    def unread(self, max_threads, query=None):
        ts = list(self.threads.values())
        if query and "is:unread" not in query:
            import re
            terms = [re.sub(r"^\w+:", "", w).lower() for w in query.split()
                     if w.upper() not in ("OR", "AND")]
            terms = [w for w in terms if w]

            def hit(t):
                blob = " ".join(m["from"] + " " + m.get("to", "") + " " + m["body"]
                                for m in t["messages"]).lower()
                return any(w in blob for w in terms)
            ts = [t for t in ts if hit(t)]
        return [{"thread_id": t["thread_id"], "snippet": t["messages"][-1]["body"][:120]}
                for t in ts[:max_threads]]

    def thread(self, thread_id, html=False):
        if thread_id not in self.threads:
            raise KeyError(f"no demo thread {thread_id}")
        t = self.threads[thread_id]
        msgs = []
        for i, m in enumerate(t["messages"]):
            msgs.append({"id": f"{thread_id}-{i}", "labels": m.get("labels", ["INBOX"]),
                         "is_draft": False, "is_sent": "SENT" in m.get("labels", []),
                         "from": m["from"], "to": m.get("to", self.address),
                         "cc": m.get("cc", ""), "reply_to": "", "date": m.get("date", ""),
                         "internal_ms": 0, "subject": m.get("subject", t.get("subject", "")),
                         "body": m["body"], "attachments": m.get("attachments", [])})
        return {"thread_id": thread_id, "messages": msgs}

    def drafts(self):
        """Drafts of this demo only: every demo writes into one demo-output folder."""
        out = []
        for tid in self.threads:
            p = os.path.join(paths.DEMO_OUT, f"{tid}.json")
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    d = json.load(f)
                out.append({"draft_id": d["draft_id"], "thread_id": d["thread_id"]})
        return out

    def create_draft(self, thread_id, to, cc, subject, body_html, text, attachments,
                     signature_html, quote=True, sender=None):
        draft_id = f"demo-{thread_id}"
        rec = {"draft_id": draft_id, "thread_id": thread_id, "from": sender or self.address,
               "to": to, "cc": cc, "subject": subject, "html": body_html, "text": text,
               "signature": signature_html or "",
               "attachments":
               [os.path.basename(a) for a in attachments], "created": time.time()}
        paths.write_private(os.path.join(paths.DEMO_OUT, f"{thread_id}.json"),
                            json.dumps(rec, indent=2))
        self._render_index()
        return {"draft_id": draft_id, "thread_id": thread_id, "in_reply_to": True,
                "signature": bool(signature_html),
                "preview": os.path.join(paths.DEMO_OUT, "index.html")}

    def delete_draft(self, draft_id):
        tid = draft_id.replace("demo-", "", 1)
        p = os.path.join(paths.DEMO_OUT, f"{tid}.json")
        if os.path.exists(p):
            os.remove(p)
        self._render_index()

    def _render_index(self):
        cards = []
        for tid, t in self.threads.items():
            p = os.path.join(paths.DEMO_OUT, f"{tid}.json")
            draft = None
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    draft = json.load(f)
            last = t["messages"][-1]
            cards.append(
                f'<section><h2>{h_lib.escape(t.get("subject", tid))}</h2>'
                f'<p class="meta">From {h_lib.escape(last["from"])} · {h_lib.escape(t.get("scenario", ""))}</p>'
                f'<pre>{h_lib.escape(last["body"])}</pre>'
                + (f'<h3>Draft reply to {h_lib.escape(", ".join(draft["to"]))}</h3>'
                   f'<div class="draft">{_safe_preview(draft["html"])}'
                   f'<div class="sig">-- <br>{_safe_preview(draft.get("signature", ""))}</div></div>'
                   if draft else '<p class="none">No draft - see the run report for why '
                                 '(flagged threads get no committing reply).</p>')
                + '</section>')
        page = ("<!doctype html><meta charset=utf-8><title>Demo inbox drafts</title>"
                "<style>body{font:15px/1.55 -apple-system,Segoe UI,sans-serif;max-width:760px;"
                "margin:32px auto;padding:0 16px;color:#1d1d1f;background:#fafafa}"
                "section{background:#fff;border:1px solid #e3e3e3;border-radius:10px;padding:20px;margin:0 0 20px}"
                "pre{white-space:pre-wrap;font:inherit;background:#f4f4f5;padding:12px;border-radius:8px}"
                ".draft{border-left:3px solid #2f6fed;padding:4px 0 4px 14px}"
                ".meta,.none{color:#666;font-size:13px}.sig{margin-top:14px;font-size:13px;color:#666}"
                "h3{font-size:14px;color:#2f6fed;margin:18px 0 6px}"
                "@media (prefers-color-scheme:dark){body{background:#161618;color:#e8e8ea}"
                "section{background:#1f1f22;border-color:#333}pre{background:#2a2a2e}"
                ".meta,.none,.sig{color:#a0a0a6}}</style>"
                "<h1>Demo inbox: drafts</h1><p class=meta>Fictional creators. Nothing was sent.</p>"
                + "".join(cards))
        paths.write_private(os.path.join(paths.DEMO_OUT, "index.html"), page)


def _safe_preview(html):
    # The draft already passed safety.scrub; this is belt and braces for a local file.
    import re
    return re.sub(r"<\s*(script|iframe|object|embed)\b.*?(</\s*\1\s*>|/?>)", "", html,
                  flags=re.I | re.S)


def participants(thread, me=DEMO_ADDRESS):
    addrs = {me}
    for m in thread["messages"]:
        for field in ("from", "to", "cc"):
            for _, a in getaddresses([m.get(field, "")]):
                if a:
                    addrs.add(a.lower())
    return addrs
