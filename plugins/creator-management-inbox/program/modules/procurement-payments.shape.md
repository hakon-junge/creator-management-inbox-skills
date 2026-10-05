# Module shape: procurement-payments (Block 1 replies)

Loads in Block 1 with `procurement-payments.md` on a payment-timing, invoice, PO,
tax-form or supplier-portal question. Every term is quoted from `deals.md`; the status
comes from the record (the note, the thread, finance's last word), never assumed.

## "When do I get paid?"

The terms counted from their trigger (`terms-from-trigger`), then the next thing the
creator will see:

> "Our terms are net 30 from the invoice - yours came in complete on the 2nd, so it falls
> due on the 1st of next month. The portal emails you a remittance note once it's paid."

Nothing on record yet (no invoice, no PO) -> what starts the clock, and how to send it.

## A missing tax form

- Name the form we collect (`{{TAX_FORMS}}`), link the tax authority's own page for the
  blank form, and point at `{{SUPPLIER_PORTAL}}` for the upload - never back by email.
- "Which one do I need?" -> which form we collect from whom (`deals.md`); anything beyond
  that is for the form's instructions or their own adviser.
- A form or tax number pasted into an email: never quote it or note it; thank them, point
  at the portal, ⚠️ so the user deletes the message.

## A PO still pending

The honest state (raised and waiting for approval, or not raised yet) and what it unblocks
("once it's issued, I'll send you the number to put on the invoice"). Asking finance about
a run is not a date: "I've asked whether it can make the next run - I'll confirm when they
reply", never "it'll be paid Thursday". Finance is chased internally (the report's ⚠️);
a creator who already had a holding note gets news or a named day, not a second one.

## Late against the terms

Check, in this order, before replying: (1) the invoice - received, complete, the right
entity, amount and currency; (2) the PO - on the invoice, approved; (3) the documents - a
tax form and the vendor set-up in the portal; (4) only then ⚠️ to finance with the
specifics. The reply names what's missing on their side, kindly and exactly ("the invoice
needs the PO number on it"); if nothing is, the honest state and a named
day for the next update. Never "it's on its way" without a payment record
(`done-claims`).

## The supplier portal

- A first invoice -> the invite comes from the portal itself: say what that email looks
  like and the one step that matters there (tax form, bank details).
- Locked out or the invite expired -> ⚠️ for the user to resend it; the reply says when
  they'll have a fresh one.
- Bank details go into the portal only; an email asking to change them is Block 0.
