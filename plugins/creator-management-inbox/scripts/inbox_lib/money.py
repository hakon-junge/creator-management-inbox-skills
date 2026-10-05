"""Money and claims checks on a draft's visible text, in code.

    committed_total(text)     -> what the draft commits: (total, currency, items)
    sign_off_limit(me_md)     -> (amount, currency) from `{{SIGN_OFF_LIMIT}}` in me.md
    check(text, cards, limit) -> {"errors": [...], "warnings": [...]}

Detection is deliberately conservative. A fee is a number WITH a currency
(740 USD, $740, USD 740, 2.4k EUR). It is multiplied only by an unambiguous count
next to it: "3 x 740 USD", "3 videos at 740 USD", "740 USD each for 3 videos",
"740 USD x 3". A stated total ("1,480 USD in total", "total: 1,480 USD") is the
headline. A fee named as a past or current figure ("your current 900 USD",
"was 900 USD", "instead of 900 USD") is a reference, not a commitment.
"""
import re
import time

NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
             "both": 2}
_NW = "|".join(NUM_WORDS)
CODES = ("USD|EUR|GBP|CAD|AUD|NZD|CHF|SEK|NOK|DKK|PLN|INR|JPY|SGD|HKD|BRL|MXN|ZAR|AED")
_SYM = r"(?:US\$|CA\$|C\$|AU\$|A\$|NZ\$|\$|€|£)"
_NUM = r"\d{1,3}(?:[,.  ]\d{3})+(?:[.,]\d{1,2})?(?!\d)|\d+(?:[.,]\d{1,2})?(?!\d)"
FEE = re.compile(
    rf"(?:(?P<sym>{_SYM})\s?(?P<n1>{_NUM})(?P<k1>[kK]\b)?(?:\s?(?P<code1>{CODES})\b)?"
    rf"|\b(?P<code2>{CODES})\s?(?P<n2>{_NUM})(?P<k2>[kK]\b)?"
    rf"|(?<![\w.,$€£])(?P<n3>{_NUM})(?P<k3>\s?[kK]\b)?\s?(?:(?P<code3>{CODES})\b|(?P<sym3>€|£)"
    r"|(?P<word>dollars|euros|pounds)\b))")
_UNITS = (r"(?:videos?|integrations?|posts?|reels?|shorts?|tiktoks?|stories|story|pieces?|"
          r"deliverables?|uploads?|episodes?|mentions?|spots?|slots?|segments?|carousels?|"
          r"newsletters?|clips?|dedicateds?|streams?|lives?)")
# A count is never half of a range or a duration: "60-90 second", "a 30-day window".
_COUNT = (rf"(?<!\d[-–])(?P<n>\d+|{_NW})(?!\s*(?:[-–]|to)\s*\d)"
          r"(?!\s*-?\s*(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?"
          r"|%|percent)\b)")
# Left of a fee: "3 x [up to 4 words] [at|for|@]" or "3 [up to 3 words] videos [at|for|:]".
_LEFT_X = re.compile(rf"\b{_COUNT}\s*[x×]\s*(?:[A-Za-z][\w'-]*\s+){{0,4}}?(?:(?:at|for|@)\s*)?$", re.I)
_LEFT_UNITS = re.compile(rf"\b{_COUNT}\s+(?:[A-Za-z0-9][\w'\-–]*\s+){{0,3}}?{_UNITS}\s*"
                         r"(?P<prep>at|for|@|of|:|-|,)?\s*$", re.I)
# Right of a fee: "each", "per video", "x 3", "each for 3 videos".
_EACH = re.compile(rf"^\s*(?:each|apiece|per\s+(?:{_UNITS}|piece|one)|/\s*{_UNITS})\b", re.I)
_RIGHT_X = re.compile(r"^\s*(?:(?:each|per\s+\w+)\s*)?[x×]\s*(?P<n>\d+)\b", re.I)
_RIGHT_UNITS = re.compile(rf"^\s*(?:each|apiece|per\s+\w+)\s+(?:for|across|over|on)\s+"
                          rf"(?:the\s+|all\s+)?{_COUNT}\s+(?:[A-Za-z][\w'-]*\s+){{0,3}}?{_UNITS}",
                          re.I)
_TOTAL_LEFT = re.compile(r"(?:\btotal(?:\s+(?:of|is|comes\s+to|would\s+be|fee))?|\bin\s+total|"
                         r"\baltogether|\boverall|\bcombined|\bpackage(?:\s+(?:of|is|at|for))?|=|"
                         r"\bcomes\s+to|\badds\s+up\s+to|\bsum\s+of)\s*[:\-]?\s*(?:is\s+)?$", re.I)
_TOTAL_RIGHT = re.compile(r"^\s*(?:in\s+total|total|altogether|overall|combined|all[- ]in|"
                          r"for\s+(?:the\s+)?(?:whole|full|entire)\s+(?:package|deal|round)|"
                          r"for\s+(?:all|both)\b"
                          rf"|for\s+(?:the\s+|all\s+)?(?:{_NW}|\d+)\b(?!\s*(?:[-–x×]|to\b)))", re.I)
_REFERENCE = re.compile(r"\b(?:current(?:ly)?|previous(?:ly)?|old|was|were|instead\s+of|"
                        r"down\s+from|up\s+from|compared\s+(?:to|with)|versus|vs\.?)\s+"
                        r"(?:(?:rate|fee|price|of|at|is|was|the|your|our|my|a|an)\s+){0,3}$", re.I)
# "$2,400 is your usual rate": their figure, named back, not our offer.
_REFERENCE_RIGHT = re.compile(r"^\s*(?:(?:is|was|were)\s+(?:your|their|his|her)\s+(?:usual\s+|normal\s+|"
                              r"standard\s+|current\s+|regular\s+|typical\s+)?(?:rate|fee|price)"
                              # "2,400 USD is a bit out of range": their figure judged, not offered.
                              r"|(?:is|was|would\s+be|feels|sits)\s+(?:a\s+(?:bit|little)\s+|well\s+|far\s+|"
                              r"way\s+|quite\s+|still\s+|just\s+)?(?:out\s+of\s+(?:range|budget|reach)|above|"
                              r"over|beyond|outside|more\s+than|higher\s+than|too\s+(?:high|much|steep)))",
                              re.I)
# "At 900 USD a video, the bar was 40": conversion-bar math, not an offer.
_BAR = re.compile(r"\b(?:bar|break-?even|threshold)\b", re.I)
_AT_LEFT = re.compile(r"\bat\s+(?:your\s+|the\s+|a\s+|our\s+)?$", re.I)
# "spend capped at 5,000 USD per post per 30 days": an ad-spend cap, not a fee to the creator.
_SPEND = re.compile(r"\b(?:ad\s+)?spend\b|\bad\s+budget\b|\bmedia\s+budget\b", re.I)
_CAP_LEFT = re.compile(r"\b(?:capped\s+at|cap\s+(?:of|at)|limit(?:ed)?\s+(?:of|to|at)|"
                       r"max(?:imum)?\s+(?:of|at)?|up\s+to)\s*$", re.I)
_PER_PERIOD_RIGHT = re.compile(r"^\s*(?:per|a|/|every)\s+(?:\w+\s+){0,3}?(?:\d+\s*)?"
                               r"(?:days?|weeks?|months?|flights?)\b", re.I)
# "- Video 2: 740 USD": an itemized line keeps its own label, so two equal fees
# on two labelled lines are two deliverables, not one fee said twice.
_LABEL = re.compile(r"^\W*(?P<label>[A-Za-z][^:\n]{0,40}):\s*$")
_SIGNOFF_LINE = re.compile(r"\[\s*DO FIRST\s*:\s*get\s+sign-?off\b[^\[\]\n]*\]", re.I)
_DO_FIRST = re.compile(r"\[\s*DO FIRST\b[^\[\]\n]*\]", re.I)
_FILL_INS = re.compile(r"\[[^\[\]\n]*\]")
_URL = re.compile(r"(?:https?://|www\.)\S+", re.I)

DOLLARS = {"USD", "CAD", "AUD", "NZD", "SGD", "HKD"}

# Rule done-claims, in code: past-tense claims that an action happened.
DONE_CLAIM = re.compile(
    r"\bpayment(?:'s|\s+is|\s+has\s+been|\s+was)?\s+(?:now\s+|already\s+|just\s+)?"
    r"on\s+(?:its|the)\s+way\b"
    r"|\bpayment\s+(?:has\s+been\s+|was\s+|'s\s+been\s+)?(?:now\s+|already\s+|just\s+)?"
    r"(?:sent|triggered|processed|released|initiated)\b"
    r"(?!\s+(?:within|after|once|when|upon|as\s+soon|every|each|in\s+\d|\d))"
    r"|\b(?:it|that|this|everything|all)(?:'s|\s+is|\s+has\s+been|'s\s+been)\s+"
    r"(?:now\s+|all\s+|already\s+)?(?:logged|updated|added|unlocked|upgraded)\b"
    r"(?!\s+(?:daily|weekly|monthly|hourly|every|each|in\s+real[- ]time|automatically|"
    r"live|regularly|once|when|whenever|after|within|value))"
    r"|\bI(?:'ve|\s+have)\s+(?:just\s+|already\s+|now\s+)?"
    r"(?:logged|updated|added|unlocked|upgraded)\b"
    r"(?!\s+(?:a\s+few\s+|a\s+couple\s+of\s+|some\s+|my\s+|the\s+|two\s+|three\s+)?"
    r"(?:notes?|comments?|feedback|thoughts|timestamps?|suggestions?|edits?|questions?|"
    r"details?|links?|points?)\b)"
    r"|\bjust\s+(?:logged|updated)\b", re.I)
_HERE = re.compile(r"\b(?:below|above|inline|in\s+this\s+email)\b", re.I)
_IF = re.compile(r"\b(?:once|when|whenever|after|as\s+soon\s+as|if|until|before)\s+$", re.I)


def parse_number(s, k=False):
    s = s.replace(" ", "").replace(" ", "").strip()
    if re.fullmatch(r"\d{1,3}([,.])\d{3}(?:\1\d{3})*(?:[.,]\d{1,2})?", s):
        sep = s[len(re.match(r"\d+", s).group(0))]
        whole, _, dec = s.replace(sep, "\x00").partition("." if sep == "," else ",")
        x = float(whole.replace("\x00", "") + ("." + dec if dec else ""))
    else:
        x = float(s.replace(",", "."))
    return x * 1000 if k else x


def _currency(m):
    code = m.group("code1") or m.group("code2") or m.group("code3")
    if code:
        return code.upper()
    sym = m.group("sym") or m.group("sym3") or ""
    word = (m.group("word") or "").lower()
    if "€" in sym or word == "euros":
        return "EUR"
    if "£" in sym or word == "pounds":
        return "GBP"
    return {"US$": "USD", "CA$": "CAD", "C$": "CAD", "AU$": "AUD", "A$": "AUD",
            "NZ$": "NZD"}.get(sym, "$")


def same_currency(a, b):
    if not a or not b or a == b:
        return True
    return {a, b} <= DOLLARS | {"$"} and "$" in (a, b)


def _count(word):
    return int(word) if word.isdigit() else NUM_WORDS[word.lower()]


def _segments(text):
    """Sentences and lines: a count never multiplies a fee across a full stop."""
    text = _FILL_INS.sub(" ", _URL.sub(" ", text))
    for line in text.splitlines():
        for seg in re.split(r"(?<=[.!?;])\s+", line):
            if seg.strip():
                yield seg


def fee_mentions(text):
    """Every fee in the text: {amount, currency, n, kind, text}. kind is
    multiplied (n x amount), total, single or reference."""
    out = []
    for seg in _segments(text):
        for m in FEE.finditer(seg):
            n_raw = m.group("n1") or m.group("n2") or m.group("n3")
            k = bool(m.group("k1") or m.group("k2") or m.group("k3"))
            try:
                amount = parse_number(n_raw, k)
            except ValueError:
                continue
            left, right = seg[:m.start()], seg[m.end():]
            label = _LABEL.match(left)
            item = {"amount": amount, "currency": _currency(m), "n": 1, "kind": "single",
                    "text": m.group(0).strip(),
                    "label": label.group("label").strip().lower() if label else None}
            lx, lu = _LEFT_X.search(left), _LEFT_UNITS.search(left)
            rx, ru = _RIGHT_X.match(right), _RIGHT_UNITS.match(right)
            start = m.start()
            if lx:
                item.update(n=_count(lx.group("n")), kind="multiplied")
                start = lx.start()
            elif lu:
                each = lu.group("prep") in ("at", "@") or _EACH.match(right)
                item.update(n=_count(lu.group("n")),
                            kind="multiplied" if each and not _TOTAL_RIGHT.match(right)
                            else "total")
                start = lu.start()
            elif rx:
                item.update(n=_count(rx.group("n")), kind="multiplied")
            elif ru:
                item.update(n=_count(ru.group("n")), kind="multiplied")
            elif _TOTAL_LEFT.search(left) or _TOTAL_RIGHT.match(right):
                item["kind"] = "total"
            if (_REFERENCE.search(seg[:start]) or _REFERENCE_RIGHT.match(right)
                    or (_BAR.search(seg) and _AT_LEFT.search(left))
                    or (_SPEND.search(seg) and (_CAP_LEFT.search(left)
                                                or _PER_PERIOD_RIGHT.match(right)))):
                item["kind"] = "reference"
            if item["kind"] == "multiplied" and item["n"] < 2:
                item["kind"] = "single"
            if item["kind"] == "multiplied":
                item["text"] = f"{item['n']} x {item['text']}"
            out.append(item)
    return out


def committed_total(text, currency=None):
    """(total, items) for the fees in `currency` (any, when None). The headline
    total wins when it is the largest figure; otherwise multiplied lines plus
    distinct other fees add up. Restatements of a line's unit price or of a
    total are not counted twice."""
    ms = [f for f in fee_mentions(text) if f["kind"] != "reference"
          and same_currency(f["currency"], currency)]
    multiplied, seen = [], set()
    for f in ms:
        key = (f["n"], f["amount"])
        if f["kind"] == "multiplied" and key not in seen:
            seen.add(key)
            multiplied.append(f)
    totals = [f for f in ms if f["kind"] == "total"]
    units = {f["amount"] for f in multiplied}
    whole = {f["n"] * f["amount"] for f in multiplied} | {f["amount"] for f in totals}
    singles, keys = [], set()
    for f in ms:
        key = (f["label"], f["amount"])
        if f["kind"] == "single" and f["amount"] not in units | whole and key not in keys:
            keys.add(key)
            singles.append(f)
    lines = sum(f["n"] * f["amount"] for f in multiplied) + sum(f["amount"] for f in singles)
    top = max([f["amount"] for f in totals] or [0])
    return max(top, lines), (multiplied + singles) or [f for f in totals if f["amount"] == top][:1]


def sign_off_limit(me_text):
    """(amount, currency) from the `{{SIGN_OFF_LIMIT}}` line of me.md, or None
    while it is TODO, none or missing."""
    m = re.search(r"`?\{\{SIGN_OFF_LIMIT\}\}`?\s*:\s*(.+)", me_text or "")
    if not m or re.match(r"\s*(todo|none)\b", m.group(1), re.I):
        return None
    value = m.group(1)
    f = FEE.search(value)
    if f:
        n_raw = f.group("n1") or f.group("n2") or f.group("n3")
        return parse_number(n_raw, bool(f.group("k1") or f.group("k2") or f.group("k3"))), \
            _currency(f)
    n = re.search(_NUM, value)
    return (parse_number(n.group(0)), None) if n else None


def _fmt(x):
    return f"{x:,.2f}".rstrip("0").rstrip(".") if x % 1 else f"{x:,.0f}"


def _numbers(text):
    """Numbers a reader sees, outside URLs and fill-in lines. Bare numbers under
    100 and four-digit years are skipped (durations, counts, dates)."""
    out = []
    for seg in _segments(text):
        fees = {(m.start(), m.end()) for m in FEE.finditer(seg)}
        for m in re.finditer(rf"(?<![\w.,])(?P<n>{_NUM})(?P<k>[kK]\b)?", seg):
            try:
                x = parse_number(m.group("n"), bool(m.group("k")))
            except ValueError:
                continue
            money = any(a <= m.start() < b for a, b in fees)
            year = re.fullmatch(r"(19|20)\d\d", m.group("n"))
            if money or (x >= 100 and not year):
                out.append((x, m.group(0)))
    return out


def check(text, cards=(), limit=False):
    """Errors for a private MAX in the draft, a total over the sign-off limit
    without its DO FIRST line, and a done-claim without a DO FIRST line.
    limit: (amount, currency), None (me.md has none: warn) or False (skip)."""
    errors, warnings = [], []
    public = {v for c in cards for v in c.get("public", [])}
    for value, raw in _numbers(text):
        for c in cards:
            if value == c.get("max"):
                when = time.strftime("%H:%M", time.localtime(c.get("ts", 0)))
                if value in public:
                    warnings.append(f"{raw} is the private MAX of the {c['format']} card "
                                    f"printed at {when} and also another card's offer - "
                                    "make sure this draft goes to that other creator")
                else:
                    errors.append(f"{raw} is the private MAX of the {c['format']} card "
                                  f"printed at {when}: MAX never goes to a creator - use "
                                  "that card's OPEN, TARGET or a ladder step")
                break

    if limit:
        amount, cur = limit
        total, items = committed_total(text, cur)
        if total > amount and not _SIGNOFF_LINE.search(text):
            t, lim = " ".join(filter(None, (_fmt(total), cur))), \
                " ".join(filter(None, (_fmt(amount), cur)))
            detail = " + ".join(f["text"] for f in items)
            errors.append(
                f"this draft commits {t} ({detail}), above the {lim} sign-off limit in "
                f"me.md: add `[DO FIRST: get sign-off for {t} - then delete this line]` "
                "where the total sits, or bring the total under the limit (rule signoff-total)")
        other = sorted({f["currency"] for f in fee_mentions(text)
                        if f["kind"] != "reference" and not same_currency(f["currency"], cur)})
        if other:
            warnings.append(f"fees in {', '.join(other)} can't be checked against the sign-off "
                            "limit in me.md (another currency) - check the total by hand")
    elif limit is None and any(f["kind"] != "reference" for f in fee_mentions(text)):
        warnings.append("me.md has no `{{SIGN_OFF_LIMIT}}` yet - the deal total was not checked")

    pending = [x for x in _DO_FIRST.findall(text) if not _SIGNOFF_LINE.fullmatch(x)]
    if not pending:
        for seg in _segments(text):
            for m in DONE_CLAIM.finditer(seg):
                if _IF.search(seg[:m.start()]) or (
                        m.group(0).lower().startswith("i") and _HERE.search(seg[m.end():])):
                    continue
                errors.append(
                    f'the draft says "{m.group(0)}": a draft calls an action done only once '
                    "it is done (rule done-claims) - add `[DO FIRST: <the action> - then "
                    "delete this line]` where the claim sits, or say it as pending")
    return {"errors": errors, "warnings": warnings}
