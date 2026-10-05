#!/usr/bin/env python3
"""Rate engine - OPEN / TARGET / MAX rate card for creator collaborations.

Single card (known creator - auto-loads views, price book, realized value):
  rate_engine.py --handle <handle> [--deliverable yt_dedicated] [--views 30000] [--ask 900]
Single card (new creator - data before number):
  rate_engine.py --platform youtube --niche <niche> --tier T1 --views 25000 \
                 --deliverable yt_integration [--ask 1200]
Bulk (re-onboarding - one row per creator x deliverable, writes rate_cards.csv):
  rate_engine.py --bulk handle1,handle2,handle3 [--csv out.csv]
  rate_engine.py --bulk-file handles.txt

Data files live in ~/.claude/inbox/rates/ (falls back to ../references, or --data):
  benchmarks.json         cohort bands + value rates. Ships EMPTY. Generate it.
  creators_snapshot.json  per-creator history. LOCAL ONLY, never committed.

Policy: MAX = 1.0x expected in-window value (proven, >= MIN_POSTS_PROVEN clean
posts) / 0.8x (new or thin); TARGET = 0.5x EV; OPEN = 0.4x EV; all bounded by the
market CPM band. Floors come from the company profile. MAX is internal only.

WITHOUT BENCHMARKS THIS SCRIPT REFUSES TO PRINT A RATE CARD. See advisory_mode().
"""
import json, argparse, math, os, sys, csv, datetime

# ============================================================================
# CONFIG - everything company-specific lives here, nothing below this block.
# Values marked FROM PROFILE are read out of benchmarks.json meta, which is
# itself generated from your warehouse. Values here are structural defaults.
# ============================================================================
CONFIG = {
    # Display. Set from your profile company.md {{CURRENCY}}.
    "currency_symbol": "$",

    # File names inside the data directory.
    "benchmarks_file": "benchmarks.json",
    "snapshot_file": "creators_snapshot.json",

    # Profile files a human has to fill. Named verbatim in error output so the
    # operator never has to guess which file is blocking them.
    "profile_economics": "~/.claude/inbox/profile/rates.md and deals.md",
    "profile_warehouse": "~/.claude/inbox/profile/data-sources.md",
    "benchmarks_path_hint": "~/.claude/inbox/rates/benchmarks.json",

    # Minimum cohort samples before a lookup is trusted. Different on purpose:
    # a percentile band survives a small n far better than a ratio of sums does.
    "min_n_value": 15,
    "min_n_cpm": 8,

    # Own-history override thresholds.
    "min_posts_proven": 4,      # >= this many clean posts -> price on their own history
    "min_posts_blend": 2,       # >= this many -> 50/50 blend with the cohort rate

    # Staleness.
    "stale_views_days": 180,    # last live post older than this -> demand fresh analytics
    "stale_bench_days": 60,     # benchmarks older than this -> warn before big tickets

    # Ladder shape. Fractions of the OPEN->TARGET gap for the two middle rungs.
    # Roughly halving increments: the conditioning says the bottom is near.
    "ladder_steps": (4 / 7, 6 / 7),
    "ladder_min_gap": 20,       # below this, a ladder is theatre - just quote TARGET
    "round_to": 10,             # rounding grain. Precise-looking beats round-looking.

    # Deliverable defaults per platform, and which codes count as short-form for
    # the floor test. Extend both if you add deliverable types.
    "dt_default": {"youtube": "yt_integration", "instagram": "ig_reel",
                   "tiktok": "tt_video", "newsletter": "nl_main"},
    "short_form": {"ig_reel", "tt_video", "yt_short", "ig_carousel",
                   "ig_static", "ig_stories", "tt_carousel"},
    "long_form_platforms": {"youtube"},
}

CUR = CONFIG["currency_symbol"]


def money(x):
    return f"{CUR}{x:,.0f}"


def r_grain(x):
    """Round to CONFIG['round_to'], half-up."""
    g = CONFIG["round_to"]
    q = x / g
    f = math.floor(q)
    return int((f if (q - f) <= 0.5 else f + 1) * g)


# ============================================================================
# LOADING + ADVISORY MODE
# ============================================================================
def bench_is_empty(B):
    """True when no cohort has any usable band or value rate."""
    b = (B or {}).get("bench") or {}
    for table in ("cpm", "value"):
        for level in (b.get(table) or {}).values():
            if level:
                return False
    return True


def advisory_mode(B, data_dir, reason):
    """Explain the calculation, name the missing inputs, refuse to quote.

    A guessed rate card is worse than no rate card: it gets quoted, it anchors
    the creator, and you cannot un-send it.
    """
    meta = (B or {}).get("meta") or {}
    pol = meta.get("policy") or {}
    floors = pol.get("floors") or {}
    print("RATE ENGINE - ADVISORY MODE. No rate card will be printed.")
    print(f"  reason: {reason}\n")
    print("  what the engine would compute, if it had the inputs:")
    print("    EV        = median organic views x cohort value-per-1k x geo multiplier")
    print("    MAX       = EV x {:.2f} (proven) / {:.2f} (new or thin history)".format(
        pol.get("ceiling_proven", 1.0), pol.get("ceiling_new", 0.8)))
    print("    TARGET    = EV x {:.2f}, bounded by the cohort's paid-CPM p75".format(
        pol.get("target", 0.5)))
    print("    OPEN      = EV x {:.2f}, bounded by the cohort's paid-CPM median".format(
        pol.get("open", 0.4)))
    print("    then floors, verdict, Ackerman ladder, conversion bar\n")
    print("  inputs it is missing:")
    missing = []
    if bench_is_empty(B):
        missing.append(f"cohort value rates and paid-CPM bands -> {CONFIG['benchmarks_path_hint']} is an empty skeleton")
    if floors.get("short_form_min") is None or floors.get("long_form_min") is None:
        missing.append("policy floors -> {{RATE_FLOOR_SHORTFORM}} / {{RATE_FLOOR_LONGFORM}}")
    if not meta.get("value_basis") or str(meta.get("value_basis", "")).startswith("TODO"):
        missing.append("the definition of the value column you are summing -> meta.value_basis")
    if not (meta.get("geo_mult_value") or {}).get("T2"):
        missing.append("measured geo multipliers -> regenerate from Q2 of refresh_queries.sql")
    for m in missing or ["(none detected - the failure is elsewhere, check the data dir)"]:
        print(f"    - {m}")
    print("\n  fill these, in this order:")
    print(f"    1. {CONFIG['profile_warehouse']}  (table and column names, and what")
    print("       'conversion' and 'value added' actually mean at this company)")
    print(f"    2. run references/refresh_queries.sql, then")
    print(f"       scripts/assemble_benchmarks.py <dir> --date YYYY-MM-DD")
    print(f"    3. {CONFIG['profile_economics']}  (floors, geo tiers, payback window,")
    print("       and whether the conversion-value yardstick may be disclosed)")
    print(f"\n  data dir searched: {data_dir}")
    print("\n  interim: negotiate from published third-party rate surveys, mark every")
    print("  deal in this period as benchmark-setting, hold the policy floors from day")
    print("  one, and refresh as soon as you have matured collaborations to measure.")
    sys.exit(2)


def load(data_dir):
    bp = os.path.join(data_dir, CONFIG["benchmarks_file"])
    if not os.path.exists(bp):
        print(f"RATE ENGINE - ADVISORY MODE. No rate card will be printed.\n"
              f"  reason: {CONFIG['benchmarks_file']} not found in {data_dir}\n"
              f"  generate it: see {CONFIG['benchmarks_path_hint']} and the refresh\n"
              f"  protocol in SKILL.md.")
        sys.exit(2)
    b = json.load(open(bp))
    p = os.path.join(data_dir, CONFIG["snapshot_file"])
    snap = json.load(open(p)) if os.path.exists(p) else {}
    return b, snap


def lookup(bench, table, platform, niche, dt, min_n):
    """Most specific cohort that clears min_n. pnd -> pn -> p."""
    for level, key in (("pnd", f"{platform}|{niche}|{dt}"),
                       ("pn", f"{platform}|{niche}"),
                       ("p", platform)):
        v = (bench.get(table) or {}).get(level, {}).get(key)
        if v and v.get("n", 0) >= min_n:
            return v, level
    return None, None


# ============================================================================
# THE CARD
# ============================================================================
def card(B, SNAP, handle=None, platform=None, niche=None, tier=None, views=None,
         dt=None, ask=None, quiet=False):
    bench, meta = B["bench"], B["meta"]
    pol = meta.get("policy") or {}
    floors_cfg = pol.get("floors") or {}
    c = SNAP.get(handle or "", {})
    platform = (platform or c.get("platform") or "").lower()
    niche = niche or c.get("niche") or "Uncategorized"
    tier = tier or c.get("tier") or "T1"
    dt = dt or CONFIG["dt_default"].get(platform, platform)
    flags, notes = [], []

    # ---- views: explicit > snapshot recent median. Never invented.
    src_views = "given"
    if views is None and c.get("med_recent_views"):
        views = c["med_recent_views"]
        src_views = "snapshot recent median"
        last = c.get("last_live")
        if last:
            age = (datetime.date.today() - datetime.date.fromisoformat(last)).days
            if age > CONFIG["stale_views_days"]:
                flags.append(f"views basis is STALE (last live post {last}) - get a fresh "
                             f"screen recording of their analytics before sending a number")
    if not platform or not views:
        raise SystemExit("need --platform and --views (or --handle with snapshot views). "
                         "No card without median organic views plus audience geo.")

    # ---- leak handling: anomalous conversion -> flag plus a stricter basis
    leak = c.get("leak_risk")
    own_allowed, own_basis_field = True, "vpp"
    if leak in ("known", "link-suspect"):
        own_allowed = False
        flags.append(f"LEAK RISK ({leak}): own history untrusted - priced on the cohort rate "
                     f"only; screen manually before any offer")
    elif leak == "promo-suspect":
        own_basis_field = "vpp_link"
        flags.append("LEAK RISK (promo-suspect): promo redemptions look leaked - recalibrated "
                     "on LINK-attributed value only")

    # ---- expected in-window value per post
    val, vlevel = lookup(bench, "value", platform, niche, dt, CONFIG["min_n_value"])
    if not val:
        raise SystemExit(
            f"no cohort value data for {platform}/{niche}/{dt} at n>={CONFIG['min_n_value']}. "
            f"Either the cohort is genuinely new (price it as a flagged test off the nearest "
            f"parent cohort, and log the outcome) or the benchmarks need a refresh.")
    gv = (meta.get("geo_mult_value") or {}).get(tier, 1.0)
    ev_cohort = views * val["r_cur"] / 1000.0 * gv
    own = c.get(own_basis_field) if own_allowed else None
    n_hist = c.get("vpp_n") or 0
    proven = own_allowed and n_hist >= CONFIG["min_posts_proven"] and (c.get("conv_win") or 0) > 0

    if own and n_hist >= CONFIG["min_posts_proven"]:
        ev = own
        basis = (f"their own realized in-window value/post ({money(own)}, {n_hist} clean posts, "
                 f"decay-weighted)")
        if c.get("med_recent_views") and views > 2 * c["med_recent_views"]:
            notes.append(f"requested views ({views:,.0f}) are >2x their recent median "
                         f"({c['med_recent_views']:,.0f}) - own-history EV may understate; "
                         f"sanity-check which post this is")
    elif own and n_hist >= CONFIG["min_posts_blend"]:
        ev = (own + ev_cohort) / 2
        basis = f"blend of their history ({money(own)}, {n_hist} posts) and the cohort rate"
    else:
        ev = ev_cohort
        basis = (f"cohort rate ({vlevel}: {val['n']} posts, {money(val['r_cur'])}/1k views "
                 f"current-regime x geo {gv:.2f})")

    ceil_mult = pol["ceiling_proven"] if proven else pol["ceiling_new"]
    max_rate = r_grain(ev * ceil_mult)
    target = r_grain(ev * pol["target"])
    open_rate = max(CONFIG["round_to"], r_grain(ev * pol["open"]))

    # ---- market band: what you actually pay in this cohort now.
    # The model says what a post is worth; the band says what it costs. Pay the lower.
    cpm, clevel = lookup(bench, "cpm", platform, niche, dt, CONFIG["min_n_cpm"])
    market = None
    if cpm:
        gm = (meta.get("geo_mult_cpm") or {}).get(tier, 1.0)
        market = {k: r_grain(views * cpm[k] * gm / 1000.0) for k in ("p25", "med", "p75")}
        open_rate = min(open_rate, market["med"]) if market["med"] > 0 else open_rate
        target = min(target, market["p75"]) if market["p75"] > 0 else target
    open_rate = min(open_rate, max_rate)
    target = min(max(target, open_rate), max_rate)

    # ---- policy floors. Not model output - they are allowed to override the model.
    floor = 0
    floor_known = True
    if dt in CONFIG["short_form"]:
        f = floors_cfg.get("short_form_min")
        floor_known = floor_known and f is not None
        floor = max(floor, f or 0)
    if platform in CONFIG["long_form_platforms"]:
        f = floors_cfg.get("long_form_min")
        floor_known = floor_known and f is not None
        floor = max(floor, f or 0)
    if not floor_known:
        flags.append(f"policy floors are unset in the profile - floor logic SKIPPED. "
                     f"Fill {{{{RATE_FLOOR_SHORTFORM}}}} / {{{{RATE_FLOOR_LONGFORM}}}} in "
                     f"{CONFIG['profile_economics']} before quoting a small deal.")

    verdict = "OK"
    if market and market["p25"] > max_rate:
        verdict = ("DECLINE-BY-MATH: even the cheap end of the market band exceeds our value "
                   "ceiling - affiliate-only offer")
    if floor and max_rate < floor:
        verdict = (f"AFFILIATE-ONLY: value ceiling ({money(max_rate)}) is below the "
                   f"{money(floor)} policy floor - do not pay a flat fee here")
    elif floor and open_rate < floor and verdict == "OK":
        open_rate = floor
        target = max(target, floor)
        notes.append(f"OPEN lifted to the {money(floor)} policy floor")

    # ---- Ackerman concession ladder. Shrinking increments, no lowball open,
    #      landing exactly at TARGET. Delivery rules live in negotiation-playbook.
    ladder = None
    if not verdict.startswith(("DECLINE", "AFFILIATE")) and target > open_rate + CONFIG["ladder_min_gap"]:
        gap = target - open_rate
        steps = [open_rate] + [r_grain(open_rate + gap * f) for f in CONFIG["ladder_steps"]] + [target]
        dedup = []
        for s in steps:
            if not dedup or s > dedup[-1]:
                dedup.append(s)
        ladder = dedup if len(dedup) >= 3 else None

    # ---- creator-facing conversion bar, TARGET basis (the one sanctioned disclosure).
    #      bar = fee / (target multiple x cohort value per conversion), so clearing it
    #      leaves the margin the target multiple implies.
    bar_div = (val.get("value_per_conversion") or 0) * pol["target"]

    def conv_bar(amount):
        return round(amount / bar_div, 1) if bar_div > 0 and amount else None

    # ---- price book anchor: the re-onboarding move
    pb = (c.get("price_book") or {}).get(dt)
    price_verdict = None
    if pb and pb.get("last_fee"):
        cur = pb["last_fee"]
        if verdict.startswith(("DECLINE", "AFFILIATE")):
            price_verdict = f"current {money(cur)} -> RESTRUCTURE (affiliate-only / performance terms)"
        elif cur > max_rate:
            price_verdict = f"current {money(cur)} is ABOVE MAX -> CUT to <= {money(max_rate)} or restructure"
        elif cur > target:
            price_verdict = f"current {money(cur)} sits between TARGET and MAX -> HOLD, do not raise"
        else:
            price_verdict = (f"current {money(cur)} is at/below TARGET -> room to keep or reward "
                             f"performance (never lead with a raise)")

    # ---- creator flags
    gv_t3 = (meta.get("geo_mult_value") or {}).get("T3")
    if tier == "T3":
        pct = f"~{gv_t3:.0%} of T1 value per view - " if gv_t3 else ""
        flags.append(f"T3 geo: {pct}affiliate-first strongly preferred")
    if not proven and own is None and not c:
        flags.append(f"no tracked history - NEW-creator ceiling ({pol['ceiling_new']:.0%} of "
                     f"expected value) applied")
    if c.get("exceptional_converter"):
        notes.append("EXCEPTIONAL converter - high but plausible conversion rate. A retention "
                     "priority, not a leak; protect the relationship")
    if c.get("trend_down"):
        flags.append("recent views trending down vs their prior posts - consider opening lower")
    if c.get("boosted_posts"):
        notes.append(f"{c['boosted_posts']} post(s) overlapped paid amplification - organic value "
                     f"may be inflated; boost economics are a separate analysis")

    ask_line = ""
    if ask:
        icpm = ask / views * 1000
        band_txt = (f"our paid band {cpm['p25']}-{cpm['p75']} CPM ({cpm.get('window','t24')})"
                    if cpm else "no band")
        if cpm and icpm < cpm["p25"]:
            rel = "BELOW our band"
        elif cpm and icpm <= cpm["p75"]:
            rel = "within band"
        else:
            rel = "ABOVE our band"
        if ask > max_rate:
            rel += " and ABOVE our ceiling"
        if ask <= open_rate:
            rel += " - BELOW our opening rate: accept, don't negotiate up"
        ask_line = f"their ask {money(ask)} = {money(icpm)} CPM ({rel}; {band_txt})"

    drift_line = None
    if cpm and cpm.get("b_now_med") and cpm.get("med"):
        drift_line = (f"market context: this cohort's paid CPM is {money(cpm['b_now_med'])}/1k in "
                      f"the current regime (band median {money(cpm['med'])}, n={cpm['n']}) - "
                      f"compare the two before you accept anyone's memory of what things cost")

    return {
        "handle": handle or "new creator", "platform": platform, "niche": niche, "tier": tier,
        "dt": dt, "views": views, "views_src": src_views,
        "ev": ev, "basis": basis, "proven": proven,
        "open": open_rate, "target": target, "max": max_rate, "ceil_mult": ceil_mult,
        "ladder": ladder, "bar_div": bar_div,
        "conv_bar_target": conv_bar(target),
        "conv_bar_current": conv_bar(pb["last_fee"]) if pb and pb.get("last_fee") else None,
        "cohort_value_per_conv": val.get("value_per_conversion"),
        "market": market, "market_level": clevel, "verdict": verdict,
        "price_book": pb, "price_verdict": price_verdict,
        "flags": flags, "notes": notes, "ask_line": ask_line, "drift_line": drift_line,
        "snapshot": c,
    }


def print_card(k):
    c = k["snapshot"]
    print(f"RATE CARD - {k['handle']} | {k['platform']}/{k['niche']}/{k['dt']} | {k['tier']} | "
          f"views {k['views']:,.0f} ({k['views_src']})")
    if c:
        print(f"  their record: {c.get('paid_posts',0)} paid posts, {money(c.get('pay_total',0))} paid | "
              f"conversions {c.get('conv_win',0):,.0f} (promo share {c.get('promo_share')}) | "
              f"CAC {money(c.get('cac') or 0)} | in-window value {money(c.get('val_win',0))} | "
              f"LTV:CAC {c.get('ltv_cac')} | ROI {c.get('roi_pct')}% | payback {c.get('payback_pct')}% | "
              f"conv/1k {c.get('conv_per_1k')}")
    print(f"  expected in-window value/post ~ {money(k['ev'])}  ({k['basis']})")
    print(f"  OPEN   {money(k['open'])}\n  TARGET {money(k['target'])}\n  MAX    {money(k['max'])}  "
          f"<- walk-away ({int(k['ceil_mult']*100)}% of expected value; never write this to the creator)")
    if k.get("ladder"):
        print(f"  ladder (contested): {' -> '.join(money(s) for s in k['ladder'])}  "
              f"(steps ~halve; empathy between rounds; limited authority once; sweetener on the last)")
    if k.get("conv_bar_target"):
        cur = f"; at their current fee: {k['conv_bar_current']}" if k.get("conv_bar_current") else ""
        print(f"  conversion bar (creator-facing, TARGET basis): {k['conv_bar_target']} conversions "
              f"in-window at the target fee{cur}  (= fee / (target multiple x cohort value per "
              f"conversion {money(k['cohort_value_per_conv'] or 0)}))")
    if k["market"]:
        print(f"  market band (paid history): {money(k['market']['p25'])} / {money(k['market']['med'])} / "
              f"{money(k['market']['p75'])}  ({k['market_level']})")
    if k["price_book"]:
        pbook = k["price_book"]
        print(f"  current price ({k['dt']}): last {money(pbook['last_fee'])} on {pbook['last_date']} "
              f"(median of last 3: {money(pbook['med_fee_last3'])}, {pbook['n_paid']} paid)")
    if k["price_verdict"]:
        print(f"  price verdict: {k['price_verdict']}")
    print(f"  verdict: {k['verdict']}")
    if k["ask_line"]:
        print(f"  {k['ask_line']}")
    for f in k["flags"]:
        print(f"  ! {f}")
    for n in k["notes"]:
        print(f"  - {n}")
    if k["drift_line"]:
        print(f"  {k['drift_line']}")
    print('\n  basis sentence: "we base our rates on a mix of your median views, audience '
          'demographics, and your niche, so it stays fair and consistent for everyone we '
          'work with"')


def bulk(B, SNAP, handles, out_csv):
    if not SNAP:
        print("! no creators_snapshot.json in the data dir - bulk mode needs per-creator history.")
        print(f"  Generate it with refresh_queries.sql Q5 + assemble_benchmarks.py. It is local")
        print(f"  only and must never be committed: it names creators alongside fees paid.")
        sys.exit(2)
    rows, errors = [], []
    for h in handles:
        h = h.strip().lower()
        if not h:
            continue
        c = SNAP.get(h)
        if not c:
            errors.append((h, "not in snapshot - check the handle, or pull live from the CRM"))
            continue
        dts = sorted((c.get("price_book") or {}).keys()) or \
            [CONFIG["dt_default"].get(c.get("platform", ""), c.get("platform", ""))]
        for dt in dts:
            try:
                k = card(B, SNAP, handle=h, dt=dt, quiet=True)
            except SystemExit as e:
                errors.append((h, f"{dt}: {e}"))
                continue
            pbook = k["price_book"] or {}
            if k["verdict"].startswith("AFFILIATE"):
                short = "AFFILIATE-ONLY"
            elif k["verdict"].startswith("DECLINE"):
                short = "DECLINE-BY-MATH"
            elif pbook.get("last_fee") and pbook["last_fee"] > k["max"]:
                short = f"CUT to <={money(k['max'])}"
            elif pbook.get("last_fee") and pbook["last_fee"] > k["target"]:
                short = "HOLD"
            elif pbook.get("last_fee"):
                short = "KEEP (below target)"
            else:
                short = "OK"
            rows.append({
                "handle": h, "name": c.get("name"), "owner": c.get("owner"),
                "lead_status": c.get("lead_status"), "platform": k["platform"], "niche": k["niche"],
                "tier": k["tier"], "deliverable": dt, "last_live": c.get("last_live"),
                "paid_posts": c.get("paid_posts"), "pay_total": c.get("pay_total"),
                "med_recent_views": c.get("med_recent_views"),
                "current_fee_last": pbook.get("last_fee"), "current_fee_date": pbook.get("last_date"),
                "current_fee_med3": pbook.get("med_fee_last3"),
                "conv_win": c.get("conv_win"), "promo_share": c.get("promo_share"),
                "cac": c.get("cac"), "val_win": c.get("val_win"), "rev_win": c.get("rev_win"),
                "ltv_cac": c.get("ltv_cac"), "roi_pct": c.get("roi_pct"),
                "payback_pct": c.get("payback_pct"), "conv_per_1k": c.get("conv_per_1k"),
                "ev_per_post": round(k["ev"]), "OPEN": k["open"], "TARGET": k["target"], "MAX": k["max"],
                "ladder": " -> ".join(money(s) for s in k["ladder"]) if k.get("ladder") else None,
                "conv_bar_current": k.get("conv_bar_current"),
                "verdict": short, "band_verdict": k["verdict"].split(":")[0],
                "price_verdict": (k["price_verdict"] or "").split("->")[-1].strip(),
                "leak_risk": c.get("leak_risk"), "trend_down": c.get("trend_down"),
                "exceptional": c.get("exceptional_converter"),
            })
    if rows:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {len(rows)} rate-card rows for {len(set(r['handle'] for r in rows))} "
              f"creators -> {out_csv}")
        for r in rows:
            cur = money(r["current_fee_last"]) if r["current_fee_last"] else "-"
            print(f"  {r['handle']:24s} {r['deliverable']:15s} cur {cur:>8s} -> "
                  f"OPEN {money(r['OPEN']):>7s} TGT {money(r['TARGET']):>7s} MAX {money(r['MAX']):>8s}  "
                  f"{r['verdict']}" + (f"  [{r['leak_risk']}]" if r["leak_risk"] else ""))
        print("\n  work the CUT and DECLINE rows first - those are the urgent conversations.")
        print("  Then hand one creator at a time to negotiation-playbook. MAX never travels.")
    for h, e in errors:
        print(f"  ! {h}: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--handle")
    ap.add_argument("--platform")
    ap.add_argument("--niche")
    ap.add_argument("--tier", choices=["T1", "T2", "T3"])
    ap.add_argument("--views", type=float, help="median ORGANIC views per post (recent posts)")
    ap.add_argument("--deliverable", default=None)
    ap.add_argument("--ask", type=float, default=None)
    ap.add_argument("--bulk", help="comma-separated handles -> CSV of rate cards")
    ap.add_argument("--bulk-file", help="file with one handle per line")
    ap.add_argument("--csv", default="rate_cards.csv")
    ap.add_argument("--data", default=None)
    a = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    if a.data is None:
        # Your data lives outside the plugin so updates never overwrite it.
        user = os.path.expanduser(os.path.join(os.environ.get("INBOX_HOME") or
                                               "~/.claude/inbox", "rates"))
        ref = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references")
        a.data = user if os.path.exists(os.path.join(user, CONFIG["benchmarks_file"])) else ref
    B, SNAP = load(a.data)

    # Refuse before computing anything. This is the guard that makes the whole
    # skill safe to hand to a new company on day one.
    if bench_is_empty(B):
        advisory_mode(B, a.data, "benchmarks.json contains no cohort bands or value rates")
    if (B["meta"].get("policy") or {}).get("target") is None:
        advisory_mode(B, a.data, "benchmarks.json meta.policy is incomplete")

    gen = B["meta"].get("generated")
    if not gen:
        advisory_mode(B, a.data, "benchmarks.json has no generation date - provenance unknown")
    age = (datetime.date.today() - datetime.date.fromisoformat(gen)).days
    if age > CONFIG["stale_bench_days"]:
        print(f"! benchmarks generated {gen} ({age}d ago) - refresh before big-ticket "
              f"negotiations (SKILL.md refresh protocol)\n")

    if a.bulk or a.bulk_file:
        handles = (a.bulk.split(",") if a.bulk else [l.strip() for l in open(a.bulk_file)])
        bulk(B, SNAP, handles, a.csv)
        return
    k = card(B, SNAP, handle=a.handle, platform=a.platform, niche=a.niche,
             tier=a.tier, views=a.views, dt=a.deliverable, ask=a.ask)
    print_card(k)


if __name__ == "__main__":
    main()
