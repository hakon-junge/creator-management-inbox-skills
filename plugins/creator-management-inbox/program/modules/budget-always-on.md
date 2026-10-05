# Module: budget-always-on (a standing program, repeat collaborations)

The always-on variant of the budget model, on by `model: always-on` or the pack default;
it never loads together with `budget-campaign-pot` for one thread (`thread_binding` in
`inbox program`). `deal_shape` is its parameter: `test-then-scale` turns on the two-piece
rule below; `ambassador` uses the itemized package (a concrete number for every
deliverable, one headline total) from the first deal, with a review point at a set date.

**Framing.** Long-term and consistent: "we price every first collaboration the same way
and aim to work together for years". The **consistency counterweight** ("consistent,
always-on pay beats sporadic campaign spikes") closes the niches-not-names play on "other
brands pay more". Re-booking is continuous: re-book when the numbers support it.

## The two-piece rule (floor AND cap; `deal_shape: test-then-scale`)

Two pieces is the standard - the minimum and the maximum on a first test: two long-form,
two short-form or two feed videos. Dropping a bigger ask to two is itself the concession
you give for holding the fee.

- **Floor - never below two; no single-piece deals.** One post is too noisy to read (a
  good creator's one flat video, a weak fit's one lucky spike).
- **Floor as retreat, never the opener.** They won't accept the two-piece price and you
  hold the number -> "same rate, one piece instead" is a no-fault exit that keeps the rate
  and the door: "if [$X for two] doesn't feel comfortable, we could do a single video at
  [$X] instead, so you're not committing to the full series before we've built any shared
  track record." (Case: offered on a first collab; the creator kept the full series at the
  held rate.)
- **Cap - never 3+ on a first test** (locking a longer run at a fee that may not fit is
  the trap): a new creator asking for 3+ is re-scoped to two as the trade for holding
  terms. For new creators the cap is non-negotiable and the escalating ladder is off.
- **The "no moonshot" lever** against a single high-fee piece: "we don't do one-off
  moonshots - I'd rather back you across two so neither of us is betting everything on a
  single upload." It makes scope a fairness argument on THEIR side (one post lives or dies
  on the algorithm's mood; two give a second at-bat).
- **In a reply to our outreach** (money-core §3, Door B): "For a first collaboration, we
  usually keep it focused - two videos where you show `{{PRODUCT}}` in your own style.
  Once we see how it lands, we scale from there."
- **Spacing (mostly new creators):** at least a week apart, ideally inside a 30-day window
  (organic signal, a paid test, a month to read before rolling on); established creators
  looser, across months.
- **D - Volume ask ("meet me at $X, lock in N videos").** NEW / not-yet-profitable ->
  decline the volume and re-scope to two (the concession for holding the fee); never
  accept three to unlock a lower per-video fee. A single high-fee piece -> the no-moonshot
  lever, pull UP to two. ESTABLISHED with a proven, profitable record -> acknowledge their
  consistency argument as correct, then reward volume with STRUCTURE, not a flat raise:
  the escalating per-video ladder (established-only; e.g. a small step up on each of three
  videos, paid only if the relationship continues).

## Late delivery: patient, gated on performance x communication

Never on the calendar. A trusted partner weeks late: first pull CURRENT performance -
results and profitability THIS YEAR, not lifetime - then read the communication.
**Performing + proactively updating, unprompted -> keep waiting** (evergreen long-tail
content; lateness costs us little): the lapsed schedule renews at the same rate while
extracting NEW value (a bonus deliverable, a repositioned slot). **Performing badly**
(more so with a bad prior deal or lost deals) **-> stop waiting:** the polite,
creator-facing parting per the pause/exit shapes (Scenario K to convert or wind down).
Performing but gone quiet -> a follow-up bump with a status ask, then the re-engagement
ladder.

## End of deal: recalibration

- **G.1 - The conversion-bar close** (lowering an established fee without friction):
  translate the economics into a plain bar the creator can see - "At $820 a video, the
  bar that video had to clear was 17 subscriptions. You landed at 15... At $700 the bar
  is 14 - and you cleared that." The cut becomes a bar they can clear (case: four videos
  recalibrated ~15% down, accepted the same day). The bar is the sanctioned exception to
  the internal-numbers rule; its definition and arithmetic come from `conversion-bar`
  (rate-engine), at both the target fee and their current fee - use its number, never
  hand-derive.
- **G.6 - The recalibrated rate is rejected.** Never a number closer to their anchor: the
  deal restructures, with the frame that makes the hold acceptable.
  - **Restructure menu (combine freely):** swap the deliverable down a format (dedicated
    -> integration; the new line may step UP slightly in unit price while the total lands
    far under their anchor - the structure holds the line); shrink the included boost
    window and price extensions at the per-30-day rate in `{{BOOSTING_TERMS}}`; stage the
    affiliate up (`{{AFFILIATE_RATE_STANDARD}}` -> `{{AFFILIATE_RATE_LAUNCH}}` now,
    conditional `{{AFFILIATE_RATE_VIP}}` for trusted long-term partners); split a surface
    out to its teammate owner (`{{TEAM_ROSTER}}`) so the core deal stays clean; park
    premium formats to a NAMED quarter.
  - **The frame (elements, not a template):** (a) recalibration, not judgment - grounded in
    THEIR numbers (results vs the bar), never a company-wide pricing policy `deals.md`
    doesn't state; (b) not personal - "the push comes from above, we fought for this
    number" only where `limited-authority` applies (once per thread, `me.md` names a
    sign-off above you); (c) TEMPORARY by design - "if performance builds, we can revisit next
    quarter", a dated or seasonal re-open; backtest the season first (a quarter that led
    conversions in two of the last three years is "typically one of our strongest
    quarters", never "always" - and check it's the season, not your budget calendar), or
    the re-open becomes a promise you're held to; (d) the fast-pay double-push - the held
    rate pays on `{{PAYMENT_SPEED_CLAIM}}`, not the market's 30-90 days (value lever 1).
    The three canonical pushback reasons: `references/plays.md`.
  - **A hybrid counter (base + performance bonus):** never invent a per-signup cash bonus;
    the performance leg goes through the affiliate percentage (incl. the conditional
    `{{AFFILIATE_RATE_VIP}}` path) and written recalibration commitments (value lever 6).
    Loyalty buys structure and upside, never a re-anchored base from our side: hand the
    structuring question back, name no new number yourself.
  - **The exit is a pause, never a break:** "We'll respect your rate - let's pause for now
    and revisit next quarter; the door stays open." Never devalue their content on the way
    out. (Internal, never written: consistent payers get scarcer in a tightening market; a
    paused creator often returns at our number.)
- **G.7 - The upfront-payment break-glass** (the LAST-resort closer; not plays.md's L,
  which holds standard terms on an upfront ask): dedicated long-term partners only
  (multi-year history), never a default, never early - only after the restructure, the
  affiliate upgrade and the value levers. Shape: "if you're comfortable holding at [the
  recalibrated rate], we'll move you back to upfront payment." Allowed in an auto-draft
  but ALWAYS ⚠️-flagged at the top of the report for sign-off before send.

## Established re-book - the package shape (reply shape)

**Re-onboarding a returning creator** leads with the onboarding step
(`{{ONBOARDING_FORM_URL}}` if they have one), references their real history, includes
their personal code and a tracking link per video, and links the brief.

Re-booking an established, trusted creator puts the FULL itemized commercial on the table
at once - **never hedge a component as "calibrated on results" or "we'll confirm later"**
(it reads as evasive). The shape (`package-pricing`): warm results recap -> the plan as
bulleted surfaces (what runs where, cadence, timing anchored to real moments like a
seasonal peak) -> **a commercial block with a concrete number for EVERY deliverable** ->
the affiliate layered on top -> **a one-line bolded headline total**: "So the full shape:
**[total] in fees + [rate] affiliate commission**". A declared exception to `aff-entry`: a
warm continuation to a proven partner is collaborative, so the whole package goes out in
one go.

- **Trade scope, not price:** a re-book fee much below the prior rate reads as a downgrade
  however it's framed - hold a healthy fee and EXPAND the scope (add a surface, bundle
  amplification) instead of cutting toward the band. (Case: a band supporting only a
  modest short-form fee; the re-book held the prior fee and added a second surface,
  amplification bundled.)
- **The one above-band exception:** a trusted partner's strategic, multi-surface
  continuation may price above the single-post band - the bands sanity-check it, they
  don't cap it, and it is never flagged "above the ceiling" (that makes the human
  re-litigate a decision already made). Nothing else is exempt from MAX and `above-band`,
  and the sign-off limit still applies (`signoff-total`).
- **Amplification** on established creators is priced and worded per `rights-pricing`
  (usage-rights module).
- **Mid-package top-up** (slots used up, they want more NOW - not an end-of-deal review):
  check the note FIRST; profitable in total AND month over month -> one more video at the
  SAME fee, confirming alignment before adding ("if you're aligned, I'll add it right away
  at the same fee to keep everything consistent"). Unlike a re-book, hold the existing fee
  for continuity, never reprice from the band (that punishes momentum). Not profitable ->
  a renewal decision (money-core), not an automatic top-up.

## Never (this module)

- Never go below two pieces, or commit to 3+ on a first test (`test-then-scale`).
- Never move toward their anchor after a rejected recalibration - restructure (G.6).
- Never offer upfront payment except as the G.7 break-glass (dedicated multi-year
  partners, last resort, ⚠️-flagged in any draft).
