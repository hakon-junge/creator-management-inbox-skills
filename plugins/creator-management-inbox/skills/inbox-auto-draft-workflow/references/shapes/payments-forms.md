**Load when:** invoice / VAT / payout-vendor / fee payment / "not paid"; an onboarding-form
question (a program's own payout terms: its module shape in the load plan)

# Payments, invoices and onboarding-form shapes

Depends on `deals.md` (`{{PAYOUT_VENDOR}}`, payment terms, gross/net) and `me.md`
(`{{FINANCE_CONTACT}}`, `{{CHAT_TOOL}}`). Finance is looped internally, never CC'd
on a creator email.

## Payments

Routine reassurance is on-brand: "I've logged everything on our side. Also just
pinged the finance team regarding the payments 🙌"

**Reassure with the creator's NEXT VISIBLE TOUCHPOINT, not our internal verbs.**
Not "I'm logging it and getting payment moving" but:

> "I just added it to the tracker, so you should receive the notification from
> `{{PAYOUT_VENDOR}}` to accept the payment early next week 🙌"

Four things happen in that sentence: the action is stated as done (true, or a
`[DO FIRST: ...]` line until it is - `done-claims`), the event
**they** will see is named, there is a soft ETA, and "notification from
`{{PAYOUT_VENDOR}}`" is hyperlinked to the public payment-process doc. Internal
verbs tell a creator that something is happening somewhere they cannot see, which
is exactly the anxiety the message is meant to remove.

"When do payments go out?" → answer with the process fact if it is known from the
thread or context; otherwise confirm it is queued and add "I'll nudge finance."

**Always OFF the creator thread:** CCing finance; amounts, terms or dates; and
anything that is a payment **dispute**. Missing, late or incorrect payment
escalates internally - draft only the warm "on it" holding note, and **with a
concrete next step**.

**Diagnose "I haven't been paid" as a TRACKER GAP first, not a finance problem.**

This is the highest-yield diagnostic in the whole payments shape. In the large
majority of cases the post was never logged, so payment never triggered. Check
the creator's note, the tracker or CRM for the creator's latest post FIRST. If it is
missing, the reply asks the creator for the live link, and logging it goes at the
top of the report as a pre-send action. Only escalate to finance once the post IS logged and payment still has not
moved.

Escalating to finance first wastes their time and delays the creator by days, for
a problem that lives entirely on our side of the tracker.

## VAT / invoice / billing-data issue

**Narrate the finance loop and relay finance's question before changing
anything.** You never touch the payout vendor yourself.

**Never invent a systems-behaviour answer.**

*Worked example of the failure:* a draft once confidently explained that "credit
notes are issued in `{{CURRENCY}}` by design" when the truth was an open bug
ticket that finance was already chasing with the vendor. The creator was told a
policy that did not exist, and the real answer arrived a week later contradicting
it.

So: before answering ANY currency, invoice or billing-mechanics question, search
the thread and recent finance context for an existing loop on that exact issue.
If one exists, the reply narrates its **true state** - "we're still waiting to
hear back from the payments team, it may be a bug. Let me double-check with
finance now" - honest status, never authoritative policy. And **never offer a
workaround** (the creator uploads their own invoice) that finance has not
ratified.

Opener:

> "Thanks for flagging this - I looped in our finance team to make sure we get it
> right. Before we change anything on the billing side, there's one thing they
> need to confirm with you: ..."

**Tax (VAT, sales tax).** Your position - gross or net, which countries - is
written once in `deals.md`. State it in every proposal to a creator where tax
applies: one sentence then prevents a whole class of dispute. Never quote tax
maths, promise when a correction lands, or decide gross-versus-net in a draft:
finance confirms the numbers, and a disputed position is relayed, not adjudicated.

## Onboarding-form questions ("how does it work / it won't let me submit")

*Only if the user runs a creator onboarding form (`{{ONBOARDING_FORM_URL}}` in
`me.md`); the user's own form wins.*

Stock explanation: "you submit the draft for review, I update the status to
approved, and then you can submit the live link." Known gotchas are stated
honestly rather than hedged, and a deadline the creator assumes exists but doesn't
is named plainly, with the real constraint.

**If you can unblock it, do it and say so:** "I've just updated the status on this
one, so you should be able to submit the live link now" (`done-claims` until it is).

**Fix the real blocker.** Do NOT offer the "just email me the live link instead"
workaround once the form itself is unblocked. Routing around your own system is
the fallback for when it genuinely cannot be fixed, never the first move - every
out-of-band submission is a record that does not exist and a payment that does
not trigger. When the form itself is broken, accept the submission out-of-band so
they aren't blocked, and say so while the form gets sorted.

## Backend actions - narrate vs flag

- **If the creator asked for it, or it unblocks their issue**, confirm it in the
  reply: "I've just upgraded your account for a free month" -
  with a `[DO FIRST: ...]` line until it's done (`done-claims`).
- **Proactive, unrequested housekeeping stays OUT of the copy.** Flag it in the
  coverage report instead. Narrating internal tidying to a creator adds noise to
  an email that had one job.
- **A shipped, generally-available feature is not a backend toggle.** "Enable
  access so I can film [feature]" → "it's live for all users now - here's where
  to find it" plus a screenshot. **Never invent an account-level enablement**
  that does not exist; the creator will go looking for the switch you described.
