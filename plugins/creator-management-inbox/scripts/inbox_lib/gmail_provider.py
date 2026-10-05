"""Gmail, through the official Gmail API and your own OAuth app.

Permissions requested (and nothing else):

    gmail.readonly  - read threads, your profile and your signature
    gmail.compose   - create and delete drafts

What that does NOT allow: deleting or trashing mail, changing labels, marking
anything read, changing settings. What it DOES still allow, because Google has
no drafts-only permission: sending. This tool has no send command, the plugin's
guard hook blocks send calls during a run, and every draft waits for a human.
See SECURITY.md for the full picture - we would rather say that plainly than
claim a guarantee Google does not offer.
"""
import base64
import mimetypes
import os
import re
from email.message import EmailMessage
from email.utils import formataddr, getaddresses, parseaddr

from . import paths

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]


class AuthError(Exception):
    pass


def _imports():
    try:
        from google.auth.exceptions import RefreshError  # noqa: F401
        from google.auth.transport.requests import Request  # noqa: F401
        from google.oauth2.credentials import Credentials  # noqa: F401
        from googleapiclient.discovery import build  # noqa: F401
    except ImportError:
        raise AuthError("Gmail libraries are not installed. Run: inbox setup")


def authorize(client_secret=paths.CLIENT_SECRET):
    """One-time browser consent. Saves YOUR token to ~/.claude/inbox/token.json
    (owner-only). Never bundled, never committed."""
    _imports()
    from google_auth_oauthlib.flow import InstalledAppFlow
    if not os.path.exists(client_secret):
        raise AuthError(
            f"No OAuth client file at {client_secret}.\n"
            "Create a Desktop OAuth client (say 'connect my Gmail' for the guide), "
            "then run: inbox import-client ~/Downloads/<the file>.json")
    flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True,
                                  authorization_prompt_message=
                                  "Opening your browser to connect Gmail...")
    paths.write_private(paths.TOKEN, creds.to_json())
    return creds


class Gmail:
    name = "gmail"

    def __init__(self):
        _imports()
        from google.auth.exceptions import RefreshError
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        if not os.path.exists(paths.TOKEN):
            raise AuthError("Gmail is not connected yet. Run: inbox auth")
        creds = Credentials.from_authorized_user_file(paths.TOKEN, SCOPES)
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError as e:
                    raise AuthError(
                        "Your Gmail connection expired or was revoked "
                        f"({e.__class__.__name__}). Run: inbox auth\n"
                        "If this happens every 7 days, your Google OAuth app is "
                        "still in 'Testing' - see 'Stop the weekly logout' in the "
                        "inbox-setup skill's connect-gmail guide.")
                paths.write_private(paths.TOKEN, creds.to_json())
            else:
                raise AuthError("Gmail token is invalid. Run: inbox auth")
        self.svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
        self._me = None
        self._aliases = None

    # --- identity -------------------------------------------------------
    def whoami(self):
        if not self._me:
            self._me = self.svc.users().getProfile(userId="me").execute()["emailAddress"]
        return self._me

    def send_as(self):
        """Verified send-as addresses (the primary one included)."""
        if self._aliases is None:
            try:
                got = self.svc.users().settings().sendAs().list(userId="me").execute()
                self._aliases = [a for a in got.get("sendAs", [])
                                 if a.get("isPrimary") or a.get("verificationStatus") == "accepted"]
            except Exception:
                self._aliases = []
        return self._aliases

    def signature(self, sender=None):
        want = parseaddr(sender or "")[1].lower()
        aliases = self.send_as()
        for a in ([a for a in aliases if a.get("sendAsEmail", "").lower() == want]
                  + [a for a in aliases if a.get("isDefault")]):
            if a.get("signature"):
                return a["signature"]
        return None

    def reply_from(self, thread):
        """From = the verified alias the thread was addressed to, else the primary."""
        aliases = self.send_as()
        addr = pick_from(thread["messages"], [a.get("sendAsEmail", "") for a in aliases],
                         self.whoami())
        name = next((a.get("displayName") for a in aliases
                     if a.get("sendAsEmail", "").lower() == addr.lower()), "")
        return formataddr((name, addr)) if name else addr

    # --- reading --------------------------------------------------------
    def unread(self, max_threads, query="is:unread in:inbox"):
        out, page = [], None
        while len(out) < max_threads:
            resp = self.svc.users().threads().list(
                userId="me", q=query, maxResults=min(100, max_threads - len(out)),
                pageToken=page).execute()
            for t in resp.get("threads", []):
                out.append({"thread_id": t["id"], "snippet": t.get("snippet", "")[:120]})
            page = resp.get("nextPageToken")
            if not page:
                break
        return out

    def thread(self, thread_id, html=False):
        """html=True adds each message's HTML part (the zero-edit score reads it)."""
        t = self.svc.users().threads().get(userId="me", id=thread_id, format="full").execute()
        msgs = []
        for m in t.get("messages", []):
            p = m.get("payload", {})
            h = _headers(p)
            msgs.append({
                "id": m["id"], "labels": m.get("labelIds", []),
                "is_draft": "DRAFT" in m.get("labelIds", []),
                "is_sent": "SENT" in m.get("labelIds", []),
                "from": h.get("from", ""), "to": h.get("to", ""), "cc": h.get("cc", ""),
                "reply_to": h.get("reply-to", ""), "delivered_to": h.get("delivered-to", ""),
                "date": h.get("date", ""), "internal_ms": int(m.get("internalDate", 0)),
                "subject": h.get("subject", ""),
                "body": _extract(p, "text/plain") or _html_to_text(_extract(p, "text/html")),
                "attachments": _attachment_names(p),
            })
            if html:
                msgs[-1]["html"] = _extract(p, "text/html")
        return {"thread_id": t["id"], "messages": msgs}

    def drafts(self):
        out, page = [], None
        while True:
            resp = self.svc.users().drafts().list(userId="me", maxResults=100,
                                                  pageToken=page).execute()
            for d in resp.get("drafts", []):
                out.append({"draft_id": d["id"],
                            "thread_id": d.get("message", {}).get("threadId")})
            page = resp.get("nextPageToken")
            if not page:
                return out

    # --- writing (drafts only) -------------------------------------------
    def create_draft(self, thread_id, to, cc, subject, body_html, text, attachments,
                     signature_html, quote=True, sender=None):
        t = self.svc.users().threads().get(
            userId="me", id=thread_id, format="metadata",
            metadataHeaders=["Message-ID", "References"]).execute()
        msgs = t.get("messages", [])
        # Reply to the latest NON-draft message. A pre-existing draft must never
        # become the In-Reply-To target, or the new draft is orphaned when that
        # draft is deleted (Gmail shows a thread chip with nothing inside).
        non_draft = [m for m in msgs if "DRAFT" not in m.get("labelIds", [])]
        last = (non_draft or [None])[-1]
        h = _headers(last.get("payload", {})) if last else {}
        mid, refs = h.get("message-id"), h.get("references", "")

        html = body_html
        if signature_html:
            html += ('<br clear="all"><div><br></div>-- <br><div dir="ltr" '
                     'class="gmail_signature" data-smartmail="gmail_signature">'
                     f'{_strip_cid(signature_html)}</div>')
        full_html = f'<div dir="ltr">{html}</div>'
        if quote and last:
            q_html, q_text = self._quote(last["id"])
            full_html += q_html
            text += q_text

        msg = EmailMessage()
        msg["To"] = ", ".join(to)
        msg["From"] = sender or self.whoami()
        msg["Subject"] = subject
        if cc:
            msg["Cc"] = ", ".join(cc)
        if mid:
            msg["In-Reply-To"] = mid
            msg["References"] = f"{refs} {mid}".strip()
        msg.set_content(text)
        msg.add_alternative(full_html, subtype="html")
        for path in attachments:
            ctype, _ = mimetypes.guess_type(path)
            main, sub = (ctype or "application/octet-stream").split("/", 1)
            with open(path, "rb") as fh:
                msg.add_attachment(fh.read(), maintype=main, subtype=sub,
                                   filename=os.path.basename(path))
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        d = self.svc.users().drafts().create(
            userId="me", body={"message": {"raw": raw, "threadId": thread_id}}).execute()
        return {"draft_id": d["id"], "thread_id": thread_id,
                "in_reply_to": bool(mid), "signature": bool(signature_html)}

    def delete_draft(self, draft_id):
        self.svc.users().drafts().delete(userId="me", id=draft_id).execute()

    def _quote(self, msg_id):
        """Gmail-style quoted history, so the draft looks hand-composed."""
        try:
            import html as h_lib
            from email.utils import parsedate_to_datetime
            m = self.svc.users().messages().get(userId="me", id=msg_id, format="full").execute()
            p = m.get("payload", {})
            h = _headers(p)
            name, addr = parseaddr(h.get("from", ""))
            try:
                when = parsedate_to_datetime(h.get("date", "")).strftime(
                    "%a, %b %d, %Y at %I:%M %p").replace(" 0", " ")
            except Exception:
                when = h.get("date", "")
            q_html = _extract(p, "text/html") or h_lib.escape(_extract(p, "text/plain")).replace("\n", "<br>")
            q_html = re.sub(r"<img\b[^>]*>", "", q_html, flags=re.I)
            q_html = re.sub(r"<\s*(script|style)\b.*?</\s*\1\s*>", "", q_html, flags=re.I | re.S)
            who = f"{name} &lt;{addr}&gt;" if name else addr
            quote_html = (f'<br><div class="gmail_quote"><div dir="ltr" class="gmail_attr">'
                          f'On {when} {who} wrote:<br></div><blockquote class="gmail_quote" '
                          'style="margin:0px 0px 0px 0.8ex;border-left:1px solid rgb(204,204,204);'
                          f'padding-left:1ex">{q_html}</blockquote></div>')
            q_text = "\n".join("> " + l for l in _extract(p, "text/plain").splitlines())
            return quote_html, f"\n\nOn {when} {name or addr} wrote:\n{q_text}\n"
        except Exception:
            return "", ""


# --- helpers -----------------------------------------------------------------
def _headers(payload):
    return {h["name"].lower(): h["value"] for h in payload.get("headers", [])}


def _extract(payload, want):
    if payload.get("mimeType") == want:
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(data).decode("utf-8", "replace") if data else ""
    for part in payload.get("parts", []) or []:
        got = _extract(part, want)
        if got:
            return got
    return ""


def _attachment_names(payload):
    names = []
    for part in payload.get("parts", []) or []:
        if part.get("filename"):
            names.append(part["filename"])
        names.extend(_attachment_names(part))
    return names


def _html_to_text(html):
    if not html:
        return ""
    t = re.sub(r"<\s*(script|style)\b.*?</\s*\1\s*>", "", html, flags=re.I | re.S)
    t = re.sub(r"<br\s*/?>|</p>|</div>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    import html as h_lib
    return re.sub(r"\n{3,}", "\n\n", h_lib.unescape(t)).strip()


def _strip_cid(html):
    html = re.sub(r"<img\b[^>]*\bsrc=[\"']cid:[^\"']*[\"'][^>]*>", "", html, flags=re.I)
    return re.sub(r'<img\b(?=[^>]*\b(?:width|height)=["\']0["\'])[^>]*>', "", html, flags=re.I)


def pick_from(messages, aliases, primary):
    """The verified alias a thread was addressed to: newest message first, our
    own sent messages by their From, everyone else's by To / Cc / Delivered-To."""
    known = {a.lower(): a for a in aliases if a}
    for m in reversed([m for m in messages if not m.get("is_draft")]):
        fields = ("from",) if m.get("is_sent") else ("to", "cc", "delivered_to")
        for f in fields:
            for _, addr in getaddresses([m.get(f, "")]):
                if addr.lower() in known:
                    return known[addr.lower()]
    return primary


def participants(thread):
    addrs = set()
    for m in thread["messages"]:
        for field in ("from", "to", "cc", "reply_to"):
            for _, a in getaddresses([m.get(field, "")]):
                if a:
                    addrs.add(a.lower())
    return addrs
