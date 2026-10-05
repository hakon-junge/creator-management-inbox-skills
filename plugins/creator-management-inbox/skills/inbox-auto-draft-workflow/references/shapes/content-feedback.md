**Load when:** a video, reel, draft or script is shared for review (every Block 2 thread)

# Content review and feedback shapes

Every script, talking-points, draft or video review routes through `content-reviewer`, the
review engine: it decides (approve as-is or a warm request-edits, never a reject) and runs
the gates and the two-block output. This file governs how the feedback gets WRITTEN;
approvals and go-live instructions: `shapes/content-golive`.

## Content review integration

- **The creator-facing draft = the reviewer's Block A, rewritten in this file's shape**
  (or the approval shape). Block B - the decision, gate results and fact-check - goes in
  the coverage report as an internal note, **never in the email**.
- <!-- rule:unseen-content -->
  **Content nobody has watched is never approved as if it was.** The approval line is a
  loud fill-in, `[APPROVE? watch first: <link>]`, which `inbox draft` reports as a
  pre-send action; the rest of the reply (go-live instruction, tracking link, form step)
  is drafted around it, so one glance at the video and the line becomes the approval or an
  edit request. The draft never claims to have watched, and praise stays generic. Run the
  reviewer on what IS checkable - script or transcript, code and offer, campaign
  must-haves - and mark the visual gates pending. **NO "I'll watch it and get back to you"
  holding replies, ever.**
- **A readable transcript provided → actually read it** and flag real issues before
  approving.
- **An un-openable text-post draft** (scheduling tool, professional network, short-text
  platform): the same `unseen-content` fill-in, plus the tracking link. Keep any
  covering-colleague CC.
- **Script stage:** review structure, hook, claims and CTA; say plainly that this is a
  script pass and the video review is still to come.
- **A linked script or brief** in a docs tool: open and read it. Base the reply on the
  actual content. Raise real issues warmly - the brand name is never spoken aloud, there
  is no CTA, the sponsor segment is missing, the offer wording is wrong. Only if it
  genuinely cannot be opened do the un-openable rules apply.
- **Reviewer flags** (a code/offer mismatch, off-limits claims, an unsaveable video, legal
  uncertainty) follow `claims-handling` in `content-reviewer`: draft and ⚠️ by default;
  Block 0 only for a regulated claim. **Don't block on a chat question.**

## Script feedback

Collaborative, options not orders, the creative handed back ("you know your audience
best").

- **Praise budget: two specific beats maximum, closed with ":)".** Name what is concretely
  good, then stop. No superlative meta-praise, no structural pat-on-the-back paragraph.
  Praise inflation makes the eventual real praise worthless.
- **A required change opens "One thing that I want to flag -"** and asks "could you please
  use...".
- **Suggestions block** gets a bolded lead-in: *"A couple of optional ideas, take or
  leave:"* then bullets opening "What do you think about..." / "Would it be possible
  to...". The optionality has to be explicit or every suggestion reads as a demand.
- **Always check the script has a clear CTA** - link plus code. Required. Right -> confirm
  the mechanic explicitly ONLY for new creators (no boilerplate for veterans). Missing ->
  flag it warmly; the fix names their code, plus the tracking link as a bare URL on its
  own line when the note or thread has it. The form step waits for the video approval. A
  final-green-light pass, a launch-campaign code or an offer that ends before the post
  date -> `shapes/content-golive` too.
- Cut redundant qualifiers - "and it never expires" when "evergreen" already said it.
- A rate or deliverable boundary gets its own bolded *"One quick logistics note:"*.

## Copyright / IP framing problem in the content

Flag it like a CTA gap: praise first, name it plainly without accusatory words ("the way
it's framed, it comes across like people can freely take and reuse someone else's
work..."), then make the fix a collaborative question ("what were you going for there?
would love to sort the best way to reframe it together") with a 🙏 on the reframe ask.

The creator almost never meant it. Treating it as a misunderstanding rather than a
violation gets it fixed faster and without damage.

## Audience-fit opt-outs

**Audience-fit opt-outs are honored instantly.**

A creator declining a campaign topic on their own audience-fit judgment gets the warm
accept plus a pivot into topic steering - beginner angles, search-friendly how-to angles -
**in the same reply**. Never a re-pitch of the declined topic.

*Worked example (fictional):* Priya passes on a campaign topic because her audience is
solo consultants, not product businesses. The reply accepts without friction and
immediately offers two angles that do fit her audience. She said no to a topic, not to
you, and treating it as the latter is how you lose a high-converting partner over one
campaign.
