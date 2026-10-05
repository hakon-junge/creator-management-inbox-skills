"""A draft body in, the HTML and plain text a reader sees out.

    paragraphs(raw)        -> plain lines become <p> blocks; existing blocks kept
    to_text(html)          -> paragraphs and list items, blank line between each
    sent_body_html(html)   -> a sent message's own words (signature and quote cut)
    normalize(text)        -> whitespace and curly quotes folded, for comparing

The draft and the sent message go through the same to_text(), so the zero-edit
score compares like with like.
"""
import html as htmllib
import re

_BLOCK = r"(?:p|div|ul|ol|li|blockquote|table|pre|h[1-6])"
_OPEN = re.compile(rf"<\s*{_BLOCK}\b[^>]*?(?<!/)>", re.I)
_CLOSE = re.compile(rf"<\s*/\s*{_BLOCK}\s*>", re.I)
_STARTS_BLOCK = re.compile(rf"^<\s*/?\s*(?:{_BLOCK}|br)\b", re.I)


def paragraphs(raw):
    """One <p> per plain line. Lines that already start a block (<p>, <ul>, <div>,
    <br> ...) are kept, and a block spread over several lines is joined into one,
    so source newlines never become hard breaks."""
    raw = re.sub(r"</?(?:html|body|head)\b[^>]*>", "", raw, flags=re.I)
    out, depth = [], 0
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if depth > 0 and out:
            out[-1] += " " + s
        elif _STARTS_BLOCK.match(s):
            out.append(s)
        else:
            out.append(f"<p>{s}</p>")
        depth = max(0, depth + len(_OPEN.findall(s)) - len(_CLOSE.findall(s)))
    return "".join(out)


def _link(m):
    href = re.search(r"href\s*=\s*([\"'])(.*?)\1", m.group(1), re.I | re.S)
    words = re.sub(r"<[^>]+>", "", m.group(2)).strip()
    url = href.group(2).strip() if href else ""
    if not url or url == words or url.startswith("mailto:") and url[7:] == words:
        return words or url
    return f"{words} \x02{url}\x03"   # <url>, restored after tags are stripped


def to_text(html):
    """Plain text: one block per paragraph or list item, a blank line between."""
    h = re.sub(r"<!--.*?-->", "", html or "", flags=re.S)
    h = re.sub(r"<\s*(script|style)\b.*?</\s*\1\s*>", "", h, flags=re.I | re.S)
    h = re.sub(r"<a\b([^>]*)>(.*?)</a\s*>", _link, h, flags=re.I | re.S)
    h = re.sub(r"\s*\n\s*", " ", h)                       # source newlines are spaces
    h = re.sub(r"<\s*li\b[^>]*>", "\n\n- ", h, flags=re.I)
    h = re.sub(r"<\s*br\s*/?\s*>", "\n", h, flags=re.I)
    h = re.sub(rf"<\s*/?\s*(?:{_BLOCK}|tr)\b[^>]*>", "\n\n", h, flags=re.I)
    h = htmllib.unescape(re.sub(r"<[^>]+>", "", h))
    h = re.sub("[\u00a0\u202f]", " ", h).replace("\x02", "<").replace("\x03", ">")
    lines = [re.sub(r"[ \t]+", " ", l).strip() for l in h.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


_CUT = re.compile(r"<(?:div|blockquote)\b[^>]*class=\"[^\"]*gmail_quote|"
                  r"<br\s+clear=\"all\"\s*/?>|<[^>]*class=\"[^\"]*gmail_signature|"
                  r"(?:<br\s*/?>|\n)\s*--\s*<br\s*/?>", re.I)


def sent_body_html(html):
    """A sent Gmail message's own body: everything before the signature and the
    quoted history Gmail appends."""
    m = _CUT.search(html or "")
    return html[:m.start()] if m else (html or "")


_QUOTES = str.maketrans({"‘": "'", "’": "'", "‚": "'", "‛": "'",
                         "′": "'", "“": '"', "”": '"', "„": '"',
                         "‟": '"', "″": '"'})


def normalize(text):
    return re.sub(r"\s+", " ", (text or "").translate(_QUOTES)).strip()
