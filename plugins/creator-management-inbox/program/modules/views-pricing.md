# Module: views-pricing (fees from median views and a CPM band)

On when the pack defaults to it or `pricing: views`; off with `budget: no-cash`. The
mechanism sentence: "median views x the rate for your niche x where your audience is",
priced by `inbox rate --views` from the CPM bands in `rates.md`.

## CPM framework (the pricing mechanism)

Every number comes from `rate-engine`. `{{CPM_BANDS}}` (per-format median paid CPMs from
your own completed collaborations, not a market survey) is directional; the METHOD -
median organic views x category CPM / 1000, geo-adjusted - is what holds.

- **Format gaps are the point:** long-form dedicated is highest; long-form integration
  about half to two-thirds of it (a swap down holds a total far under their anchor, G.6);
  short-form well below; Feed / Reel lowest, value side worse than paid - where most asks
  fail the value ceiling it's boost inventory, not a tracked-CAC buy (say so first).
- **Newsletters, podcasts, community posts:** no CPM from video views - price per
  placement (list or audience size), on conversions or a flat fee; never invent a CPM.
- **Regenerate the table** with every benchmark rebuild: views per dollar move fast, and a
  two-year-old band underprices you in a falling market (wrong, not conservative).
- **Geo:** the paid side uses `{{GEO_TIER_1}}` / `{{GEO_TIER_2}}` / `{{GEO_TIER_3}}`; the
  value side is steeper (`{{GEO_VALUE_MULTIPLIERS}}`), so the lowest tier is
  affiliate-first, not flat-fee. Never merge the two sets: the divergence is the signal.

**How the engine prices a views-based post:**
```
band      = median organic views / 1000 x CPM (low / typical / high) x geo multiplier
OPEN      = low end            TARGET = typical            MAX = high end
```

With `value_per_1k_views` set, value caps the band - MAX <= 80% of value (100% if proven),
TARGET <= 50%, OPEN <= 40%: **the band is what a post costs, the value what it's worth;
pay the lower.**

- **MAX at the value ceiling is break-even** - a walk-away, not a target. **TARGET at half
  the value** must clear (returns run strong well below the value line, flat near it,
  negative above; measure on your own deals). **OPEN below TARGET** leaves one ladder of
  room (lower reads as a lowball; at TARGET every concession is margin).
- **Verdicts:** MAX under the floor prints **`AFFILIATE-ONLY`** (the affiliate module's
  exit rung, or a warm pass); a low value per view usually prints `DECLINE-BY-MATH`.
  **Implied CPM** (ask / (median views / 1000)) explains the gap - never the band tables.
- **Data before number:** median ORGANIC views for **the format in question** (a TikTok
  median says nothing about a YouTube integration) + audience geo; **no card without
  both.** Never re-ask for data they gave (it costs a week and looks disorganised).
- **Star reviewers** asking many multiples of the band: usually DECLINE-BY-MATH or
  affiliate-first on a first collab; an audience that is exactly your customer, with
  content that stays up, is worth a capped test, result logged.
- **Organic only:** the fee is on ORGANIC reach (boosted views are another conversation);
  a screen recording (not screenshots) of organic vs boosted; show the math on any gap.
- **The CPM is an anchor to calibrate from, a fiscal-responsibility tool - NOT a per-view
  payment formula:** the number flexes within the bands, the BASIS doesn't. Stated, it's
  always three elements, never just "views" (a meter running): "we base our rates on a mix
  of your median views, audience demographics, and your niche, so it stays fair and
  consistent for everyone we work with." A first offer ends on one calibrated question:
  "I'm genuinely curious how close or far off that is from where you were thinking."
- <!-- override:first-number --> **Who names the first number, `views`:** median views and
  audience knowable (their note, the thread, public channel numbers) -> lead with your own
  read and invite a sense-check (it shows the work); not knowable -> ask once for the
  data, with the reason. Never ask their rate just to avoid naming yours.
- **New-surface honeymoon:** hot early metrics on a channel or account under ~3 months old
  (100+ followers/day, 10%+ engagement in month one) are new-account distribution, not
  conversion proof: price it as a controlled test and recalibrate ONLY on our tracked
  conversions. Multi-account creators fragment attribution across handles and DM funnels:
  settle the links and codes the deal requires before paying for the surface.

## The net-new ladder (first money conversation, fee-paying programs)

Net-new only (the core's recorded-fact test); a returning creator never runs this ladder.

- **The gate:** median views (note, thread or public numbers; long-form first) vs
  `{{TRACK_GATE_MEDIAN_VIEWS}}` in `deals.md` - under -> **Track A**, affiliate first
  (affiliate module off -> no Track A: a warm pass, door open); at or above -> **Track
  B**, flat fee first. (Below the gate, two pieces' conversions are noise; recompute the
  gate when bands or customer value move, and record it in `deals.md`.)
- **Precedence:** the creator names a number before we do -> no gate: the calculator,
  anchor low against their figure, never open affiliate-only (a non-answer once they've
  priced themselves); affiliate re-enters per `aff-entry`; unbridgeable -> the graceful
  walk-away. **Naming is not asking:** "what's your budget?" or "send your proposed rate"
  still runs the gate.
- **Track A (under the gate):** (1) open at **`{{AFFILIATE_RATE_STANDARD}}` affiliate
  only**, no flat fee (tracked link, promo code, the pack's offer), **two pieces** (the
  standard in both tracks; one piece is the A3 retreat, never the opener); (2) ACCEPT ->
  in the confirming reply, upgrade unprompted to **`{{AFFILIATE_RATE_LAUNCH}}`** and say
  so ("I went back and pushed for you"); (3) PUSH BACK -> the lift to
  `{{AFFILIATE_RATE_LAUNCH}}` (`limited-authority` if it applies), optionally the
  single-piece retreat (the sanctioned floor-as-retreat); (4) REJECT ->
  **`{{CASH_FLOOR_FIRST_DEAL}}` flat as "creative support" +
  `{{AFFILIATE_RATE_LAUNCH}}`**, conditional on the longer boosting window in
  `{{BOOSTING_TERMS}}`; hold.
- **Track B (at or above):** (1) open at **max(the calculator's lowest rung,
  `{{CASH_FLOOR_FIRST_DEAL}}`)** - the calculator governs above the floor, never below -
  flat fee only, **affiliate not mentioned**; two-piece test, then recalibrate; (2) "the
  fee is too low" -> layer in **`{{AFFILIATE_RATE_STANDARD}}` affiliate** with the
  conversion math on the lowest annual plan + the shorter window in `{{BOOSTING_TERMS}}`;
  (3) ACCEPT -> upgrade unprompted to `{{AFFILIATE_RATE_LAUNCH}}`; (4) REJECT ->
  `{{AFFILIATE_RATE_LAUNCH}}` in the response, no further ask; hold; no rate lands -> the
  affiliate exit rung. `{{CASH_FLOOR_FIRST_DEAL}}` is the cash floor on any first deal,
  either track, set where the effort stops feeling worth it (less buys resentment).
- **Lever order:** the rungs are the CONCESSION sequence, not a licence to skip the stack:
  spend the closing value levers at the pushback rung (A3, B2) **before** conceding
  commission points (value is free; points cost margin every time). Written commitments is
  the lever for the hold: use it at B4. Close every rung open ("would it be
  unreasonable...?"), never take-it-or-leave-it.

## Plays

- **C, per-1K** (big-gap decline): "we typically pay no more than $X per 1K median views;
  your median lands us at $Y - I fear this is way too far off for you."
- **J - They dispute the mechanism ("you shouldn't price on views").** Correct the misread
  first: we do NOT pay per view (the anchor above). It keeps the program sustainable so we
  can keep investing in creators who perform - so we value long-term repeat collaborations
  over one-off moonshots. Bring the data: the mechanism is proven across many
  collaborations over years and updated constantly. Acknowledge what numbers don't capture
  (creative process, energy, vision), then hold: no raw flat-fee inflation; reward through
  affiliate + the value levers. Can't accept the basis -> no-fault exit.

## Never (this module)

- Never expose band tables, MAX or the value ceiling; per-1K framing is fine in a C
  decline.
