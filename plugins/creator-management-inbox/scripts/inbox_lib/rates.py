"""Simple-mode rate engine: OPEN / TARGET / MAX from YOUR OWN rate bands.

Reads the ```rates block in profile/rates.md. No warehouse needed. (Teams with a
data warehouse can use the advanced engine in skills/rate-engine/scripts/.)

    band      = median views / 1000 x CPM (low / typical / high) x geo multiplier
    OPEN      = the low end            (where you open)
    TARGET    = the typical end        (where you want to land)
    MAX       = the high end           (private walk-away - never shared)

If you also know what 1,000 views earn you (value_per_1k_views), the value of the
post caps the band: MAX <= 80% of expected value (100% for a proven creator),
TARGET <= 50%, OPEN <= 40%. You pay the lower of "what the market charges" and
"what the post is worth".

Policy floors win over the model. If MAX lands under the floor, the verdict is
AFFILIATE-ONLY: the post is too small to pay a flat fee for.

A creator's ask (--ask) is read against the printed OPEN / TARGET / MAX, and
`x_max` = ask / MAX feeds the playbook's above-band routing.

A budget cap (--budget, or the campaign pot's share) caps OPEN / TARGET / MAX too.
With more than one geo tier in rates.md the tier is required: an unknown audience
must not default to the most expensive market (`blend` averages the tiers).
"""
import csv
import math
import os
import re
import statistics

_BLOCK = re.compile(r"```rates\s*\n(.*?)```", re.S)
_KV = re.compile(r"(\w+)=([^\s]+)")

SHORT = ("short", "tiktok", "reel", "story", "stories")


class RatesError(Exception):
    pass


def load(profile_dir):
    path = os.path.join(profile_dir, "rates.md")
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        raise RatesError(f"no rates.md in {profile_dir}. Say 'set up my rates'.")
    m = _BLOCK.search(text)
    if not m:
        raise RatesError("rates.md has no ```rates block")
    cfg = {"formats": {}, "geo": {}, "value": {}, "currency": None, "floors": {}}
    for raw in m.group(1).splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, rest = [x.strip() for x in line.split(":", 1)]
        kv = dict(_KV.findall(rest))
        if key == "currency":
            cfg["currency"] = rest
        elif key.startswith("geo_"):
            mult = rest.split()[0] if rest else ""
            cfg["geo"][key[4:].upper()] = {"mult": mult, "countries": kv.get("countries", "")}
        elif key.startswith("floor_"):
            cfg["floors"][key[6:]] = rest
        elif key == "value_per_1k_views":
            cfg["value"] = kv
        elif {"low", "typical", "high"} <= set(kv):
            cfg["formats"][key] = kv
    return cfg


def _num(v, what):
    try:
        x = float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        raise RatesError(f"{what} is not set yet ({v!r}). Say 'set up my rates'.")
    if x < 0 or math.isnan(x):
        raise RatesError(f"{what} must be a positive number")
    return x


def _precise(x, floor=0, ceil=None):
    """Round to a precise-looking figure: 1,240 reads as calculated, 1,250 reads as
    invented and invites a round-number counter. Never rounds below `floor`: a
    policy floor beats the precise look (400 stays 400 when the floor is 400).
    Never rounds above `ceil` (a budget cap) unless that would cross the floor."""
    if x < 100:
        r = max(int(round(x)), int(math.ceil(floor)))
        return min(r, int(ceil)) if ceil is not None and ceil >= floor else r
    step = 10 if x < 5000 else 50
    r = int(round(x / step) * step)
    if r < floor:
        r = int(math.ceil(floor / step) * step)
    if r % 50 == 0 and r - step >= max(floor, 1):
        r -= step
    while ceil is not None and r > ceil and r - step >= floor:
        r -= step
    return r


# Human format names for the basis sentence: youtube_integration -> YouTube integration.
_BRANDS = {"youtube": "YouTube", "tiktok": "TikTok", "instagram": "Instagram", "ugc": "UGC",
           "linkedin": "LinkedIn", "twitch": "Twitch", "x": "X", "facebook": "Facebook",
           "pinterest": "Pinterest", "snapchat": "Snapchat", "podcast": "podcast"}


def format_name(fmt):
    words = [w for w in re.split(r"[_\s-]+", fmt.lower()) if w]
    if not words:
        return fmt
    if words[1:] == ["dedicated"]:
        return f"dedicated {_BRANDS.get(words[0], words[0])} video"
    if words[:2] == ["youtube", "short"]:
        return "YouTube Short"
    return " ".join(_BRANDS.get(w, w) for w in words)


def _article(name):
    return "an" if name[:1].lower() in "aeio" else "a"


def geo_multiplier(cfg, tier):
    """(multiplier, label) for an audience tier. More than one tier in rates.md and
    none given -> refuse: guessing T1 prices an unknown audience at the top market."""
    geo = cfg["geo"]
    names = ", ".join(sorted(geo))
    if tier is None:
        if len(geo) > 1:
            raise RatesError(f"pass --tier: rates.md defines {names} (where the audience "
                             "is, not where the creator lives); unknown -> ask for their "
                             "audience stats, or --tier blend to average the tiers")
        if not geo:
            return 1.0, None
        tier = next(iter(geo))
    if tier.lower() == "blend":
        if not geo:
            return 1.0, "BLEND"
        mults = [_num(g["mult"], f"geo_{t}") for t, g in sorted(geo.items())]
        return sum(mults) / len(mults), "BLEND"
    g = geo.get(tier.upper())
    if g is None:
        if geo:
            raise RatesError(f"no geo tier '{tier}' in rates.md (tiers: {names}, or blend)")
        return 1.0, tier.upper()
    return _num(g["mult"], f"geo_{tier.upper()}"), tier.upper()


def quote(cfg, fmt, views, tier=None, ask=None, proven=False, budget=None,
          views_kind="average", renewal=False):
    """budget = (amount, why) or None: the most this piece may cost."""
    if fmt not in cfg["formats"]:
        raise RatesError(f"no band for '{fmt}'. Formats in rates.md: "
                         + (", ".join(cfg["formats"]) or "none"))
    band = cfg["formats"][fmt]
    lo, typ, hi = (_num(band[k], f"{fmt} {k}") for k in ("low", "typical", "high"))
    fee_band = band.get("unit") == "fee"
    if fee_band:
        # Rate-card programs: the band is already a fee, views and geo are optional.
        mult, tier_label = 1.0, tier.upper() if tier else None
        views = _num(views, "views") if views else 0
        k = 1.0
    else:
        if views is None:
            raise RatesError("this format is priced from views - pass --views (median organic views)")
        mult, tier_label = geo_multiplier(cfg, tier)
        views = _num(views, "views")
        k = views / 1000 * mult
    open_, target, max_ = lo * k, typ * k, hi * k
    basis = "market band"

    vp = cfg["value"].get(fmt)
    ev = None
    if fee_band:
        basis = "your fee range"
    elif vp and "TODO" not in vp:
        ev = _num(vp, f"value_per_1k_views {fmt}") * k
        max_ = min(max_, ev * (1.0 if proven else 0.8))
        target = min(target, ev * 0.5)
        open_ = min(open_, ev * 0.4)
        basis = "market band capped by post value"

    cap = None
    if budget is not None:
        cap, why = _num(budget[0], "budget"), budget[1]
        if max_ > cap:
            basis += f"; capped by {why}"
        open_, target, max_ = min(open_, cap), min(target, cap), min(max_, cap)

    # A format's own floor wins; UGC is priced per asset, never on the long-form floor.
    if fmt in cfg["floors"]:
        floor_key = fmt
    elif "ugc" in fmt:
        floor_key = "ugc"
    else:
        floor_key = "shortform" if any(s in fmt for s in SHORT) else "longform"
    floor = cfg["floors"].get(floor_key)
    floor = _num(floor, f"floor_{floor_key}") if floor and "TODO" not in floor else 0
    verdict = "NEGOTIATE"
    if max_ < floor:
        verdict = "AFFILIATE-ONLY"
    elif ev is not None and lo * k > ev * (1.0 if proven else 0.8):
        verdict = "DECLINE-BY-MATH"
    if cap is not None and cap < floor:
        basis += f" (under the {floor_key} floor: no flat fee fits)"
    open_, target = max(open_, floor), max(target, floor)
    target = min(target, max_) if verdict == "NEGOTIATE" else target
    open_ = min(open_, target)

    # Rounding never takes OPEN, TARGET or a ladder rung under the policy floor.
    # MAX keeps its honest value when it sits under the floor (AFFILIATE-ONLY).
    mfloor = floor if verdict == "NEGOTIATE" else 0
    p_open, p_target, p_max = (_precise(open_, floor, cap), _precise(target, floor, cap),
                               _precise(max_, mfloor, cap))
    ladder = []
    if verdict == "NEGOTIATE":
        gap = target - open_
        ladder = [p_open, _precise(open_ + gap * 0.55, floor, cap),
                  _precise(open_ + gap * 0.85, floor, cap), p_target]
        ladder = sorted(set(ladder))

    name = format_name(fmt)
    card = {"format": fmt, "views": int(views), "tier": tier_label, "geo_mult": round(mult, 3),
            "currency": cfg.get("currency"), "basis": basis, "verdict": verdict,
            "open": p_open, "target": p_target, "max_private": p_max,
            "floor": floor or None, "ladder": ladder, "budget_cap": cap,
            # No figures: a fee band's high end IS the private MAX.
            "basis_sentence": (f"For {_article(name)} {name} we work from our rate card for "
                               "that format; where you land depends on scope and usage."
                               if fee_band else
                               f"For {_article(name)} {name} we start from your {views_kind} "
                               f"of about {int(views):,} views per video and where your "
                               # The mechanism only: a "we price everyone the same way"
                               # claim belongs to the user's own program pitch, if they make it.
                               f"audience is."),
            "rules": ["MAX is private - never write it to a creator",
                      "every number travels with its mechanism (views x rate x audience)",
                      "creators move the price, you move the deliverable"]}
    if ask is not None:
        # Judge the ask against what we would actually pay (the value-capped
        # OPEN / TARGET / MAX printed above), never the uncapped market band:
        # an ask can sit inside the market band and still be far over MAX.
        a = _num(ask, "ask")
        implied = a / (views / 1000) / mult if views and not fee_band else None
        if verdict != "NEGOTIATE":
            read = f"{verdict} - no flat-fee counter, whatever the ask"
        elif a <= p_open:
            read = "at or below OPEN - good deal"
        elif a <= p_target:
            read = "at or below TARGET - reasonable"
        elif a <= p_max:
            read = "between TARGET and MAX - negotiate down"
        else:
            read = "above MAX - push back or re-scope (playbook rule above-band)"
        card["ask"] = {"amount": a, "implied_cpm": round(implied, 2) if implied else None,
                       "read": read, "over_max": a > p_max,
                       "x_max": round(a / p_max, 2) if p_max else None}
    return card


def bands_from_csv(path):
    """Build low/typical/high CPM bands from past deals.
    CSV columns (header row): format, fee, views. Extra columns are ignored."""
    by = {}
    with open(os.path.expanduser(path), newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            r = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
            try:
                fee = float(r["fee"].replace(",", "").lstrip("$€£"))
                views = float(r["views"].replace(",", ""))
            except (KeyError, ValueError):
                continue
            if views <= 0 or fee <= 0:
                continue
            by.setdefault(r.get("format", "unknown").lower().replace(" ", "_"), []).append(
                fee / views * 1000)
    out = {}
    for fmt, cpms in by.items():
        cpms.sort()
        if len(cpms) < 3:
            out[fmt] = {"n": len(cpms), "note": "fewer than 3 deals - too thin to set a band"}
            continue
        q = statistics.quantiles(cpms, n=4, method="inclusive")
        out[fmt] = {"n": len(cpms), "low": round(q[0], 2), "typical": round(q[1], 2),
                    "high": round(q[2], 2),
                    "note": "trust grows with n; 8+ deals per format is a solid band"}
    return out
