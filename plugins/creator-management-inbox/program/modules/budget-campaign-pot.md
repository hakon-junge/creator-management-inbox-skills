# Module: budget-campaign-pot (campaigns, seasonal moments, a set pot)

The campaign variant of the budget model, on by the pack default, `model: campaigns` or
`seasonal`, or `budget: monthly-pot` / `campaign-pot`. A thread binds to it when it's tied
to a named campaign, brief or seasonal moment (`thread_binding`); it never loads together
with `budget-always-on` for one thread.

| Answer | Framing | Late delivery | Re-booking |
|---|---|---|---|
| `campaigns` | Anchored to the campaign: its dates, brief and goal. Real deadlines are a real lever; never invent one. **No "for years" claims and no consistency counterweight** - replace it with what you genuinely offer: a clear brief, fast payment, results shared, first call on the next campaign (also the close on "other brands pay more"). | Firm: a video after the campaign window is worth much less - it loses most of its value. Pin dates early and hold them. | Per campaign: "we'd love you on the next one" + `{{CAMPAIGN_CALENDAR}}`. |
| `seasonal` | As campaigns, plus booking early for the moment ("spots for the January reset are filling"), only if true. | Firm around the moment. | Offer the next moment in the calendar. |

## The campaign window

`{{CURRENT_CAMPAIGN}}` holds the dates. Every date in a reply sits inside them, counted
back from the post window: brief out, product shipped (the seeding lead time), draft due,
approval, the post window itself, the dates the code is live. Name the window in the
offer ("posting between the 3rd and the 14th") so a yes is a yes to the dates too.
`{{CURRENT_CAMPAIGN}}` still `none` -> no window claimed; ⚠️ "fill program.md: campaign".

## The pot and each creator's share

**The budget sentence** (`monthly-pot` / `campaign-pot`): "We have a set budget for this
campaign across several creators, so we price everyone the same way within it." **Never
reveal the pot, its size, what's left of it or other creators' fees.**

- **Each creator's share is an internal cap:** `{{CAMPAIGN_BUDGET}}` /
  `{{CREATORS_PER_CAMPAIGN}}`. `inbox rate` applies it (`budget_cap` on the card), so
  OPEN, TARGET and MAX already sit under it. Never named, never hinted ("we're near the
  end of the budget"), never given as the reason - the reason is the mechanism.
- The share covers everything the draft commits: the fee plus priced rights and
  exclusivity lines, and product cost only if `deals.md` says it counts.
- An offer that would go above the share -> ⚠️ for the user, don't draft past it: a
  creator worth more is the user's call to move the pot, never the draft's.
- The pot is your limited authority - once per thread (`limited-authority`).

## A moved date

- Still inside the window -> the reschedule shape (`shapes/scheduling`).
- **Outside the window: convert or pass** - never the full campaign fee for a post after
  the moment by default. One offer per draft (`one-move-per-draft`), ⚠️ in the report:
  1. the next campaign in `{{CAMPAIGN_CALENDAR}}` on the same terms - only if one exists;
  2. a swap to a deliverable that can still land inside the window (stories instead of a
     reel, a shorter cut);
  3. a partial fee for what lands in the window, or a clean pass under
     `{{CANCELLATION_TERMS}}` (`shapes/cancellations`).
- Pick by what's true: a creator worth keeping and a next campaign -> 1; days left in the
  window -> 2; neither -> 3. Never invent a deadline or a consequence.

## Re-booking and the next campaign

- Per campaign, never "for years": "we'd love you on the next one", with its dates from
  `{{CAMPAIGN_CALENDAR}}` - only a campaign that is actually planned.
- Booking early for a moment ("spots are filling") only when it's true.

## Never (this module)

- Never name the pot, a creator's share, what's left or another creator's fee.
- Never draft an offer above the share, or accept a post-window date at the full fee by
  default.
- Never claim longevity ("for years") or invent a deadline or a scarcity.
