**Load when:** a rate, budget, counter, renewal, re-book, giveaway, agency list
or amplification-as-a-deal

# Money core - the inbox-side gate and shape

STRATEGY comes from `negotiation-playbook`, NUMBERS from `inbox rate` (`rate-engine`'s card
guide), the program's reply shapes from the load plan's modules; this file adds the
creator-record gate and the renewal, new-creator and giveaway shapes.

## 1. The creator-record gate comes FIRST

On ANY rate, re-engagement or renewal thread - before pricing, before the calculator,
before a counter - read the creator's note (`inbox creator <handle|email|code>`; a CRM or
dashboard if the team has one). Its `status` and results drive the decision.

**Status `do-not-re-onboard`, a record of lifetime loss, or dormant** (no post in 12+
months): do NOT negotiate and do NOT run the calculator - a graceful exit, the active
modules' no-fee door at most, never a counter-offer. *Exception:* `cut` with a live
continuation conversation is RECALIBRATED, not exited - the cut flow in §2, and a rejected
recalibration runs the budget module's pushback loop.

- **Warm, engaged creator actively asking to continue** -> the carefully written pause
  (the playbook's exit): reply warmly to the concrete items first (their video went live,
  their data question), then the transparent market-recalibration frame, pause-not-break
  with a dated or seasonal re-open, and the no-fee door if one exists. **Never
  content-quality language.** Mark ⚠️ in the report with the numbers from their note.
- **Cold or transactional thread** -> the written graceful decline, door open.
- **No note and no record at all** -> treat as new: data before number.

**Cleared for negotiation** (`continue` / `re-onboard` / `test`, or new): `inbox rate
--format <format> --ask <their_ask>`, with the inputs the pricing module names (`--proven`
for good results on record). OPEN to open, TARGET to land, MAX the internal walk-away -
**never MAX or the breakeven to a creator.** A no-flat-fee verdict (`DECLINE-BY-MATH`, or
MAX under the floor) means the active modules' no-fee path or a warm pass, never a
flat-fee counter: the band is the market's price, not your ceiling. `rates.md` not set
up -> no number in the draft: ask for their current stats (a screen recording of their
analytics), say a proposal follows, ⚠️ "set up rates". Which play an ask gets: the
playbook's `above-band` routing; either way one offer per draft (`one-move-per-draft`).

<!-- rule:signoff-total -->
**Totals and sign-off.** What the draft commits (fee x pieces + priced add-ons) above
`{{SIGN_OFF_LIMIT}}` (`me.md`) -> `[DO FIRST: get sign-off for <total> - then delete this
line]` where the total sits, top of the report; `inbox draft` refuses the total without it.
<!-- rule:no-invented-spec -->
**No invented specs:** a deliverable's length, format or count comes from the brief,
`deals.md` or the creator; worked examples illustrate a move, their details are never terms.

## 2. Renewals and end-of-deal (collaboration review)

**Trigger:** the creator shares the final video, says the last deliverable is live, or the
deal looks finished. **Confirm with data, not vibes** (the note or the user's data source,
deal and post stages): completed, or exactly one unreleased post the creator says is live
→ run this flow; 2+ unreleased → still live. **Never a "we need a few weeks to review"
holding reply** - the data does the diligence now, in this run.

**Flow:** confirm the stage → pull performance in the program's success metric from the
note, the thread or the user's data source (never estimate; none on record -> the recap
asks the user, ⚠️) → read status, fee history and module fields, `inbox rate --renewal` → map:

| Decision | Action |
|---|---|
| **Continue** (profitable, converting, active) | Re-book. Open at the rate engine's open rate, hold toward target. A gap or an overdue post → nudge to reschedule or re-book. Draft directly. |
| **Re-onboard** (profitable but dormant) | Re-approach from open toward target. No results history → price as new from `inbox rate` for their geo tier. |
| **Test** (new, no data) | Run the booked test post at the opening rate; review at day 14 for short-form, day 30 for long-form. **No big renewal pitch yet.** |
| **Cut** (rate not supported) | Do NOT renew at the current rate. Transparent value-versus-cost math, plus the active modules' no-fee track. Rejected → the pushback loop, **never a number moving toward their anchor**. Posts still booked at the old rate → decide-before-go-live: honour and wind down / renegotiate to open-target / terminate. ⚠️ flag. |
| **Do not re-onboard** | Don't re-approach. A cold inbound → graceful no-fee pivot, in writing. Warm and actively asking → the written pause per §1. ⚠️ flag. |
| **Watch** | Nudge or monitor per the decision reason. No renewal commitment. |

- **Freshness.** Results in a note are a snapshot: older than the latest video -> say so in
  the report and draft on what's known. A live instruction from the human always wins.
- **Autonomy: ALL of these get drafted**, cut and cold do-not-re-onboard included. Cut
  repricing, wind-downs, no-fee pivots and any number far from prior terms go at the TOP
  of the report under ⚠️; the human's send is the sign-off (above the limit: `signoff-total`).
- **Recap on renewal and recalibration openers** (the standing transparency commitment):
  specific results with numbers → warmth on the history → next step; direction from the
  gate, never "same terms". Attach the user's one-page recap (copy it to
  `~/.claude/inbox/attachments/`, `--attach`) and put key numbers inline (the bar, results);
  no recap file -> numbers inline plus "detailed breakdown coming", ⚠️. A downward
  recalibration without the data attached starts an argument.
- **Re-onboard / continuation draft:** warm returning opener → no-gap framing → the
  package (N videos over a date range, tied to what's fresh to cover) with rate and
  structure **from the rate engine and the note**, never "same setup as before" if it was
  repriced → a rights offer only if the usage module's history check passes → dates as
  bullets anchored to campaigns, framed as their benefit → the onboarding form, bolded,
  hyperlinked → low-pressure close → an optional p.s. on their latest video.
- **DEAL-FIRST on an acceptance:** the deal is set up (CRM record, tracker row) **before**
  the acceptance goes out, so the onboarding-form link rides in the SAME email - one
  exchange instead of two. This workflow doesn't create deals: a link that depends on a
  deal record -> `[ONBOARDING FORM LINK - create deal first]` and "create the deal -> paste
  form link" at the TOP of the report; every link that doesn't depend on the deal (join
  link, walkthrough, brief) still rides in this email; a form link that is the same for
  everyone (`{{ONBOARDING_FORM_URL}}`) goes in directly. The report proposes the note's new terms.
- **A surface another teammate owns** (newsletter, community): CC and @mention them inline.
- **Pause / not the right moment:** warm, specific about results, "not the right moment to
  continue" (never quality), a genuine door, open.

## 3. A new creator replies to your outreach

- **Yes, but no numbers, or "tell me more" - two doors.** **Default = Door B, data
  first:** the first-deal scope (the budget module sizes it), then the reason for the data
  ask, plainly: the fee is based on their real audience rather than a flat guess, so could
  they send a quick screen recording of their audience stats (recent performance, audience
  countries) - plus the brief if there is one, and "once I have those, I'll come back with
  the full details and timeline." **Door A, anchor fast** - only when the pricing inputs
  are in hand (thread, note, or public on the channel) AND `inbox rate` returns NEGOTIATE:
  OPEN with its mechanism ("based on your channel's current performance, we'd love to
  start at [OPEN] per video and grow from there"), plus what they get beyond the fee (the
  pack's creator offer). Anything uncertain -> Door B: one extra round-trip costs less
  than a bad anchor.
- **They name a rate** -> §1's gate (they're new), `inbox rate` with their ask, then
  `above-band`.

## 4. Giveaways and sponsorship contributions

Qualify first, then size deliberately: warm recognition of the tradition or the
relationship → **qualify before committing**, with the real reason stated (is the
product used throughout, or a prize on the side? - worth very different amounts, and
invisible from the request) → an un-doable side-ask gets a plain "not something we can
set up at the moment", door open → piggyback the live campaign as genuine timing.

**Sizing - NEVER autonomous, every giveaway flagged.** Draft a PROPOSED tier: start **one
tier below what was asked**, **never cash** (the pack names the tiers); central product
usage can justify matching the ask. State it positively in bold, zero apology, zero
comparison, closed with "Would that work for you?" ⚠️ every giveaway draft at the top of
the report with the proposed tier for sign-off: discretionary spend with no attribution
attached is exactly the category that needs a human on it.
