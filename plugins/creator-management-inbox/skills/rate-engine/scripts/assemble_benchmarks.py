#!/usr/bin/env python3
"""Assemble the rate-engine reference files from the refresh query outputs.

Inputs (working dir, produced by references/refresh_queries.sql):
  cohorts.json      - Q1 cohort tables (levels pnd/pn/p/d)
  geo_cells.json    - Q2 platform x niche x tier cells
  drift.json        - Q3 year x platform unit economics
  backtest.json     - Q4 pay/EV policy backtest
  snapshot_all.json - Q5 per-creator aggregates (merge the halves first)

Outputs, written into the working dir:
  benchmarks.json        - copy this back into ../references/ and commit it
  creators_snapshot.json - LOCAL ONLY. Names creators alongside fees paid, CAC
                           and realized value. Never commit it, never mail it,
                           never paste it into a chat. It is covered by
                           .gitignore for a reason.

Usage: python3 assemble_benchmarks.py [workdir] [--date YYYY-MM-DD]
"""
import json, sys, os, statistics

# ============================================================================
# CONFIG - the only place company-specific or judgement-call values appear.
# ============================================================================
CONFIG = {
    # ---- estimator constants (methodology, portable as-is) -----------------
    # Shrinkage strength: r_cur = (n_now*r_now + K*rw) / (n_now + K).
    # K is "how many current-period posts it takes before the history stops
    # dominating". 25 is a deliberate middle: responsive to a real regime
    # change within a quarter, but immune to three lucky posts in a thin cohort.
    "k_shrink": 25,

    # Minimum samples. Different on purpose - see SKILL.md.
    "min_n_value": 15,   # a ratio of sums; one outlier moves it a long way
    "min_n_cpm": 8,      # a percentile; far more robust at small n

    # Geo-cell minimums for measuring multipliers, and the priors used when a
    # cell is too thin to measure. The priors are conservative placeholders, not
    # findings - if you are still using them after two refreshes, your cells are
    # too narrow and you should measure at platform level instead.
    "min_cell_n": 6,
    "min_cell_views": 50000,
    "geo_prior": {"T2": 0.70, "T3": 0.40},

    # ---- leak detection (calibrate on your own distribution) ---------------
    # Two-sided by design: an absolute floor stops small numbers tripping the
    # flag, a share/rate test stops large legitimate creators tripping it.
    # These are starting defaults. After your first refresh, plot conversions
    # per 1k views across the corpus and put the link-leak rate threshold where
    # the distribution's tail actually separates - it will not be the same
    # number at every company or on every platform.
    "promo_abs_low": 30,      # promo-only conversions, with...
    "promo_share_high": 0.70, # ...a dominant promo share
    "promo_abs_high": 100,    # or a much larger absolute count, with...
    "promo_share_low": 0.50,  # ...a bare majority share
    "link_abs": 40,           # link conversions, with...
    "link_rate_per_1k": 10.0, # ...an implausible rate per 1k views
    "exceptional_rate": 4.0,  # high-but-plausible band: retention priority, NOT a leak

    # Confirmed leaks, carried forward between refreshes. Operational judgement,
    # so it lives here and in benchmarks.json meta.exclusions.known_leaks rather
    # than being re-derived. Keep this in sync with the IN-list in
    # refresh_queries.sql ({{KNOWN_LEAK_HANDLES}}).
    "known_leaks": [],
    # Handles a human screened and cleared: {"handle": "why, and who decided"}.
    # Recording the clearance stops the next refresh re-flagging them.
    "cleared": {},

    # ---- policy floors: FROM THE PROFILE, not from the data ----------------
    # Fill from your profile: rates.md (floors) and deals.md (value basis)
    # ({{RATE_FLOOR_SHORTFORM}} / {{RATE_FLOOR_LONGFORM}}). Left as None the
    # engine skips floor logic and says so loudly.
    "floor_short_form": None,
    "floor_long_form": None,

    # ---- value basis: describe what you actually summed ---------------------
    # Fill this sentence. "Predicted lifetime value", "realized value to date"
    # and "cash collected" are three different columns at most companies and the
    # walk-away ceiling changes by a multiple depending on which one you used.
    "value_basis": None,

    # ---- input file names ---------------------------------------------------
    "f_cohorts": "cohorts.json",
    "f_geo": "geo_cells.json",
    "f_drift": "drift.json",
    "f_backtest": "backtest.json",
    "f_snapshot": "snapshot_all.json",
    "profile_economics": "~/.claude/inbox/profile/rates.md and deals.md",
}

wd = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "."
gen_date = None
for i, a in enumerate(sys.argv):
    if a == "--date" and i + 1 < len(sys.argv):
        gen_date = sys.argv[i + 1]
if not gen_date:
    sys.exit("--date YYYY-MM-DD is required. The engine refuses benchmarks with no "
             "provenance, and a date you had to type is a date you had to think about.")


def load(name):
    p = os.path.join(wd, name)
    if not os.path.exists(p):
        sys.exit(f"missing input: {p}\nRun the matching query in "
                 f"references/refresh_queries.sql and save its rows as JSON.")
    return json.load(open(p))


def num(x):
    if x is None or x == "":
        return None
    return float(x)


K = CONFIG["k_shrink"]

# ---------------------------------------------------------------- cohorts
cohorts = load(CONFIG["f_cohorts"])
bench = {"cpm": {"pnd": {}, "pn": {}, "p": {}, "d": {}},
         "value": {"pnd": {}, "pn": {}, "p": {}, "d": {}}}
for r in cohorts:
    lvl, key = r["level"], r["cohort_key"]

    # CPM band: prefer the trailing-24m window, fall back to all-history and
    # flag it. An all-history band on a fast-moving platform is a museum piece,
    # but it beats having no band at all.
    if int(r["b24_n"]) >= CONFIG["min_n_cpm"]:
        band = {"p25": num(r["b24_p25"]), "med": num(r["b24_med"]), "p75": num(r["b24_p75"]),
                "n": int(r["b24_n"]), "window": "t24"}
    elif int(r["ball_n"]) >= CONFIG["min_n_cpm"]:
        band = {"p25": num(r["ball_p25"]), "med": num(r["ball_med"]), "p75": num(r["ball_p75"]),
                "n": int(r["ball_n"]), "window": "all"}
    else:
        band = None
    if band:
        band["b_now_med"] = num(r["bnow_med"])
        band["b_now_n"] = int(r["bnow_n"])
        # absolute fee median, for cohorts where most rows have no view count
        band["fee_med"] = num(r["fee24_med"]) if int(r["fee24_n"]) >= CONFIG["min_n_cpm"] \
            else num(r["feeall_med"])
        bench["cpm"][lvl][key] = band

    # Value rate: current-regime estimate = current-period rate shrunk toward
    # the decay-weighted history.
    vr_n = int(r["vr_n"])
    if vr_n >= CONFIG["min_n_value"] and num(r["w_v_per_1k"]) is not None:
        rw = num(r["w_v_per_1k"])
        r_now = num(r["vnow_v_per_1k"])
        n_now = int(r["vnow_n"])
        r_cur = ((n_now * r_now) + K * rw) / (n_now + K) if (r_now is not None and n_now > 0) else rw
        sw = num(r["w_s_per_1k"])
        s_now = num(r.get("snow_per_1k"))
        s_cur = ((n_now * s_now) + K * sw) / (n_now + K) if (s_now is not None and n_now > 0) else sw
        bench["value"][lvl][key] = {
            "r_cur": round(r_cur, 2), "rw": rw, "r_now": r_now, "n_now": n_now,
            "s_cur": round(s_cur, 3) if s_cur is not None else None,
            "value_per_conversion": num(r["w_value_per_conv"]),
            "n": vr_n, "n_eff": num(r.get("vr_neff")),
            "prof_window": num(r["prof_window"]),
        }

# ------------------------------------------------- geo multipliers (measured)
# Measured WITHIN platform x niche cells against that cell's T1, then the median
# across cells. Comparing tiers globally would just measure which tier your
# cheapest platform happens to skew to.
cells = load(CONFIG["f_geo"])
bycell = {}
for c in cells:
    bycell.setdefault((c["platform"], c["niche"]), {})[c["tier"]] = c

cpm_ratios, val_ratios = {"T2": [], "T3": []}, {"T2": [], "T3": []}
for cell, tiers in bycell.items():
    t1 = tiers.get("T1")
    if not t1 or t1["n_cpm"] < CONFIG["min_cell_n"]:
        continue
    r1v = (t1["v_sum"] / t1["views_sum"]) if t1["views_sum"] else None
    for t in ("T2", "T3"):
        tv = tiers.get(t)
        if tv and tv["n_cpm"] >= CONFIG["min_cell_n"] and t1["med_cpm"]:
            cpm_ratios[t].append(tv["med_cpm"] / t1["med_cpm"])
        if tv and r1v and tv["views_sum"] and tv["views_sum"] > CONFIG["min_cell_views"] and r1v > 0:
            val_ratios[t].append((tv["v_sum"] / tv["views_sum"]) / r1v)

geo_mult_cpm = {"T1": 1.0}
geo_mult_value = {"T1": 1.0}
geo_measured = {}
for t in ("T2", "T3"):
    geo_mult_cpm[t] = round(statistics.median(cpm_ratios[t]), 2) if cpm_ratios[t] \
        else CONFIG["geo_prior"][t]
    geo_mult_value[t] = round(statistics.median(val_ratios[t]), 2) if val_ratios[t] \
        else geo_mult_cpm[t]
    geo_measured[t] = {"cpm_cells": len(cpm_ratios[t]), "value_cells": len(val_ratios[t])}
    if not val_ratios[t]:
        print(f"! geo multiplier for {t} is NOT measured - falling back to the CPM ratio or "
              f"the prior. Widen the cells or accept that {t} pricing is a guess.")

# The corpus mixes tiers, so a cohort value rate is not a pure T1 rate. This
# factor says how much higher a pure-T1 rate would be. It is reported and
# deliberately NOT applied: it is dominated by whichever platform/tier pool has
# near-zero value per view, and applying it would overstate T1 EV at cohort level.
tot_v = sum(c["v_sum"] for c in cells)
tot_views = sum(c["views_sum"] for c in cells)
t1_v = sum(c["v_sum"] for c in cells if c["tier"] == "T1")
t1_views = sum(c["views_sum"] for c in cells if c["tier"] == "T1")
blend_factor_t1 = round((t1_v / t1_views) / (tot_v / tot_views), 3) \
    if t1_views and tot_views and tot_v else None

drift = load(CONFIG["f_drift"])
backtest = load(CONFIG["f_backtest"])

if CONFIG["floor_short_form"] is None or CONFIG["floor_long_form"] is None:
    print(f"! policy floors are unset in CONFIG. The engine will skip floor logic and say so.")
    print(f"  Fill them from {CONFIG['profile_economics']} before quoting small deals.")
if not CONFIG["value_basis"]:
    print("! CONFIG['value_basis'] is unset. Write down exactly which value column you summed "
          "and over what window - the walk-away ceiling depends on it.")

meta = {
    "generated": gen_date,
    "engine_version": 2,
    "value_basis": CONFIG["value_basis"] or
        "TODO - name the value column, the attribution window, and whether promo-code "
        "conversions are allocated to in-window posts.",
    "rate_estimator": {
        "name": "current-regime shrinkage",
        "formula": f"r_cur = (n_now*r_now + k*rw)/(n_now + k), k={K}",
        "rw": "recency-weighted full history, half-life 12 months",
        "r_now": "current-regime pooled rate, mature posts only",
        "why": "creator marketing goes through regime changes - conversion per view and "
               "views per dollar each move by multiples inside a year. Pure decay-weighting "
               "lags a regime change; a pure current-period rate is far too thin on small "
               "cohorts. Shrinkage buys the responsiveness of one and the stability of the "
               "other, and washes the prior out as n_now grows.",
    },
    "policy": {
        "ceiling_proven": 1.0, "ceiling_new": 0.8, "target": 0.5, "open": 0.4,
        "anchor": "median -> p75 of cohort CPM per negotiation doctrine",
        "floors": {
            "short_form_min": CONFIG["floor_short_form"],
            "long_form_min": CONFIG["floor_long_form"],
        },
    },
    "geo_mult_cpm": geo_mult_cpm,
    "geo_mult_value": geo_mult_value,
    "geo_measured_cells": geo_measured,
    "geo_value_blend_factor_t1": blend_factor_t1,
    "geo_note": "T1 = 1.0 by design: cohort value rates are already T1-heavy, so T2/T3 act as "
                "discounts only. The cross-platform T1 uplift is reported "
                "(geo_value_blend_factor_t1) and deliberately NOT applied.",
    "exclusions": {
        "known_leaks": CONFIG["known_leaks"],
        "leak_suspects_conv": [],   # filled below from the snapshot pass
        "cleared": CONFIG["cleared"],
        "auto_rules": {
            "promo_leak": "promo-only conversions >=%d with promo share >=%.0f%%, or >=%d with "
                          "share >=%.0f%%" % (CONFIG["promo_abs_low"], CONFIG["promo_share_high"] * 100,
                                              CONFIG["promo_abs_high"], CONFIG["promo_share_low"] * 100),
            "link_leak": "link conversions >=%d at >=%.0f per 1k views on social platforms"
                         % (CONFIG["link_abs"], CONFIG["link_rate_per_1k"]),
            "exceptional_converter": ">=%d link conversions at %.0f-%.0f per 1k views - a "
                                     "retention priority, not a leak"
                                     % (CONFIG["link_abs"], CONFIG["exceptional_rate"],
                                        CONFIG["link_rate_per_1k"]),
        },
    },
    "corpus": {},              # filled below
    "drift_year_platform": drift,
    "backtest_pay_vs_ev": backtest,
    "notes": [
        "Read backtest_pay_vs_ev pooled_roi_pct, not profitable_share - the portfolio is "
        "hit-driven and the most profitable bucket can have a low win rate.",
        "Read drift_year_platform before arguing with anyone about what things cost now.",
    ],
}

# ---------------------------------------------------------- creator snapshot
snap_rows = load(CONFIG["f_snapshot"])
out = {}
auto_link_leaks = []
for r in snap_rows:
    h = r["handle"]
    if not h:
        continue
    paid = int(r["paid_posts"] or 0)
    conv_win = num(r["subs_win_total"]) or 0.0
    promo_win = num(r["promo_s_win_total"]) or 0.0
    link_s_social = num(r.get("link_s_win_social")) or 0.0
    views_social = num(r.get("views_social")) or 0.0
    conv_rate = (link_s_social / views_social * 1000) if views_social > 0 else None

    known = str(r.get("known_leak")) == "1" or h in CONFIG["known_leaks"]
    promo_leak = str(r.get("leak_suspect")) == "1"
    link_leak = bool(conv_rate and link_s_social >= CONFIG["link_abs"]
                     and conv_rate >= CONFIG["link_rate_per_1k"])
    exceptional = bool(conv_rate and link_s_social >= CONFIG["link_abs"]
                       and CONFIG["exceptional_rate"] <= conv_rate < CONFIG["link_rate_per_1k"])
    if link_leak and h not in CONFIG["cleared"]:
        auto_link_leaks.append(h)

    pay_total = num(r["pay_total"]) or 0.0
    val_win = num(r["val_win_total"]) or 0.0
    rev_win = num(r["rev_win_total"]) or 0.0

    # price book: most recent paid fees per deliverable - the re-onboarding anchor
    pb = json.loads(r["price_book"]) if r.get("price_book") else []
    price_book = {}
    for e in pb:
        recent = e.get("recent_paid") or []
        fees = [num(x["pay"]) for x in recent if x.get("pay") is not None]
        price_book[e["dt"]] = {
            "n_paid": e["n_paid"],
            "last_fee": fees[0] if fees else None,
            "last_date": recent[0]["d"] if recent else None,
            # median of the last three, not the mean: one panic-priced deal
            # should not become the anchor you renegotiate against
            "med_fee_last3": round(statistics.median(fees[:3]), 0) if fees else None,
            "recent": [{"fee": num(x["pay"]), "views": num(x["views"]), "date": x["d"]}
                       for x in recent[:3]],
        }

    rv = (json.loads(r["recent_views"]) if r.get("recent_views") else []) or []
    rv = [num(x) for x in rv if x is not None]
    med_recent_views = round(statistics.median(rv[:5]), 0) if rv else None
    # trend flag: last three materially below the three before them
    trend_down = bool(len(rv) >= 6 and statistics.median(rv[:3]) < 0.6 * statistics.median(rv[3:6]))

    out[h] = {
        "name": r["name"], "platform": r["platform_latest"], "niche": r["niche"],
        "tier": r["tier"], "country": r["country"], "owner": r["owner"],
        "lead_status": r["lead_status"], "latest_deal_stage": r["latest_deal_stage"],
        "is_affiliate": r["aff_rate"] is not None, "aff_rate": num(r["aff_rate"]),
        "lt_posts": int(r["lt_posts"]), "paid_posts": paid,
        "posts_12m": int(r["posts_12m"] or 0),
        "first_live": r["first_live"], "last_live": r["last_live"],
        "pay_total": pay_total,
        "views_total": num(r.get("views_total")), "views_paid_total": num(r.get("views_paid_total")),
        "conv_win": round(conv_win, 1), "promo_conv_win": round(promo_win, 1),
        "promo_share": round(promo_win / conv_win, 2) if conv_win > 0 else None,
        "val_win": round(val_win, 0), "rev_win": rev_win,
        "link_val_win": num(r["link_v_win_total"]),
        "cac": round(pay_total / conv_win, 0) if conv_win > 0 and pay_total > 0 else None,
        "ltv_cac": round(val_win / pay_total, 2) if pay_total > 0 else None,
        "roi_pct": round((val_win - pay_total) / pay_total * 100, 0) if pay_total > 0 else None,
        # cash payback is the honest twin of ROI: val_win may be a prediction,
        # rev_win is money that actually arrived
        "payback_pct": round(rev_win / pay_total * 100, 0) if pay_total > 0 else None,
        "conv_per_1k": round(conv_rate, 2) if conv_rate is not None else None,
        "vpp": num(r["vpp"]), "vpp_link": num(r["vpp_link"]), "vpp_n": int(r["vpp_n"] or 0),
        "vpp_basis": "decay12m-in-window-value",
        "med_recent_views": med_recent_views, "trend_down": trend_down,
        "boosted_posts": int(r["boosted_posts"] or 0),
        "leak_risk": ("known" if known else
                      "promo-suspect" if promo_leak else
                      "link-suspect" if (link_leak and h not in CONFIG["cleared"]) else None),
        "exceptional_converter": exceptional,
        "promo_conv_lifetime": num(r.get("promo_s_lifetime")),
        "price_book": price_book,
    }

meta["exclusions"]["leak_suspects_conv"] = sorted(auto_link_leaks)
meta["corpus"] = {
    "posts_with_golive": sum(v["lt_posts"] for v in out.values()),
    "paid_posts": sum(v["paid_posts"] for v in out.values()),
    "creators": len(out),
    "utm_join_rate": None,   # fill from the Q1 join-rate check - see refresh_queries.sql trap 1
    "boost_flagged_handles": sum(1 for v in out.values() if v["boosted_posts"]),
}

json.dump({"meta": meta, "bench": bench},
          open(os.path.join(wd, "benchmarks.json"), "w"), indent=1)
json.dump(out, open(os.path.join(wd, "creators_snapshot.json"), "w"), indent=0, sort_keys=True)

print("benchmarks.json cpm cohorts:", {lvl: len(v) for lvl, v in bench["cpm"].items()},
      "| value:", {lvl: len(v) for lvl, v in bench["value"].items()})
print("geo_mult_cpm:", geo_mult_cpm, "| geo_mult_value:", geo_mult_value,
      "| t1 blend factor (reported, not applied):", blend_factor_t1)
print("creators:", len(out), "| with price book:",
      sum(1 for v in out.values() if v["price_book"]))
print("leak flags:", {k: sum(1 for v in out.values() if v["leak_risk"] == k)
                      for k in ("known", "promo-suspect", "link-suspect")},
      "| exceptional:", sum(1 for v in out.values() if v["exceptional_converter"]))
print("\nnext: copy benchmarks.json into ../references/ and commit it.")
print("      creators_snapshot.json stays local - it names creators alongside fees paid.")
print("      Screen any new link-suspect by hand before pricing off cohort rates, and record")
print("      cleared verdicts in CONFIG['cleared'] so the next refresh does not re-flag them.")
