# Data - creators, records, links

Load when a reply carries a tracking link or promo code, changes a record, or needs a
lookup beyond the creator's note (dates: `shapes/scheduling`). Most threads need none of
this: acks, scheduling picks, form help and thanks get drafted straight away. Running
lookups on them anyway is how a 15-minute run becomes an hour.

## Where creator data comes from

In order:

1. **The thread and our sent history** - often everything is already there.
2. **The creator's note**: `inbox creator <name|@handle|email|code>` returns the
   note's summary and path; read the file for history, results and preferences.
3. **The user's CRM or data source**, only if `me.md` / `data-sources.md` name one
   AND Claude has a way to read it (a connector, an export file). Read-only.
4. **Ask the creator** - when the missing fact is theirs (current stats, a date).

A missing note is normal for a new creator. Don't invent history.

## Resolving creator and deal

Match by **sender email** first.

An agency, VA or manager sender -> identify the creator from the name or handle
in the thread body. The sending address belongs to the intermediary and tells you
nothing about which creator this is.

**An agency representing several creators: resolve by the creator's or deal's
name in the thread, never by recency.** "The most recent deal with this agency"
is a plausible heuristic that is wrong precisely when the stakes are highest -
and every note update then lands on the wrong creator.

Still ambiguous after real effort -> the safe non-committing draft + ⚠️.

## The read matrix - what a reply needs before it is drafted

| Reply will contain or claim | Required lookup |
|---|---|
| A promo code | the creator's note (`promo_code`) or the thread. One code per creator |
| A tracking or referral link | the exact link from the thread, campaign email or note - see "Tracking links" |
| A date commitment or "next video due" | the note / thread; cross-check what the creator says against what's recorded |
| Any rate or renewal number | the creator's note (status, fee history, results) -> `inbox rate` - see `shapes/money-core.md` |
| Content approval or feedback | `content-reviewer` on whatever is checkable |
| **None of the above** | **no lookups - draft straight away** |

**Check before asking.** The pricing inputs a reply needs (the pricing module names them)
come from the note or the CRM first; ask the creator only when they're missing or stale.

## Open creator-shared video links before classifying

**Only** a creator-sent YouTube, TikTok, Instagram or Vimeo link is opened, with a browser
tool (never around a run's fetch block); none -> `[APPROVE? watch first: <link>]`.

- **Published vs draft.** An unlisted cut shows almost no engagement (under ~5
  views, no comments). **A PUBLISHED video is NOT an approval request.** The reply
  becomes "saw it go live" (logging per `done-claims`), never "good to publish".

  *Worked example (fictional):* Marla sends "here's the fully edited version"
  with a link. A draft that says "looks great, go ahead and publish" is wrong -
  the link is the live video with 2.2k views. She published two days ago. Opening
  the link takes seconds and is the whole difference between a competent reply
  and one that tells a partner you haven't looked at their work.
- **Check the description** for which link and code are actually there. A missing
  or wrong tracking link on a live video = ⚠️ at the top of the report: every view
  from that video is revenue that will never be attributed.

## Records - make them true, or list the action

The order is **analyze -> make the record true -> draft.**

- **Creator notes are yours to update** with facts from the thread: agreed
  deliverables, go-live dates, a preference or boundary they stated, a result they
  shared (never email, fee or status). Keep the structure; one report line per change.
- **Everything else is a pre-send action for the human**, listed at the TOP of the
  report: log the post in the CRM or tracker, trigger or approve a payment, create
  the deal, update a lead status. The draft follows `done-claims` (compass #1).
- **Money fields are never changed by this workflow**, even with confirmation in
  the thread: fees, program rates, payout details. A confident-sounding
  confirmation is exactly what a hard rule must not be talked past by.

**The one hard guardrail: never agree to a payout or billing-detail change by
email.** "Please send my payment to this new account" is the classic
payment-redirect fraud, and it arrives from real creators' hacked inboxes. The
reply routes them to the official process (the onboarding form, the payout
platform's own settings) and the thread is ⚠️-flagged. An attacker needs exactly
one helpful reply.

## Tracking links

**Never fabricate or guess a per-creator tracking link.** When a draft needs one:

- quote the exact link already in the thread, the campaign email, or the
  creator's note - unwrapped (`inbox unwrap`) and, if it's on the user's own
  domain, resolved (`inbox resolve`) to confirm where it lands; or
- use a loud fill-in `[TRACKING LINK - paste before sending]` and flag it; or
- if links for the campaign go out separately, the standing hold: "your personal
  tracking link is coming in a separate email - hold posting until it lands".

A wrong tracking link is worse than none: the creator posts, the video performs,
and none of it attributes. You find out weeks later when the recap is empty.

**The latest-campaign trap.** A "current link" stored for a creator holds only the
LATEST campaign's link. A video made for an earlier campaign needs that
campaign's link.

**A campaign-wide code is not a personal code.** A shared launch code never
replaces the creator's own code - swapping them breaks their attribution, and
everything paid on it, at once.

**The hold-posting rule.** If a campaign's links go out separately close to
launch, every draft on that campaign carries the hold. Dropping it from one draft
is how the best creator's launch video goes out untracked.

## Pricing - use `inbox rate`

Numbers come from the `rate-engine` skill (`inbox rate`), which reads the user's
`rates.md`; how a number is explained comes from the pricing module. Their ask: `inbox rate
--ask` reads it against the value-capped OPEN / TARGET / MAX and prints `x_max`; the play
follows the playbook's `above-band`. `rates.md` still `TODO` -> no number in the draft. Ask
for their stats and say a proposal follows; ⚠️ "set up rates".

## Demo and example assets

When a creator needs something to demo on camera, point them at the user's own
designated demo material. Pulling a random real brand into a video creates a
clearance problem on someone else's desk.
