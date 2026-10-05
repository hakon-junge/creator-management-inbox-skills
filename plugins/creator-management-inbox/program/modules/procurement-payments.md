# Module: procurement-payments (POs, tax forms, net terms, a supplier portal)

On by the pack default (ecommerce, b2b). Terms: `deals.md` - `{{NET_TERMS}}`,
`{{PO_PROCESS}}`, `{{TAX_FORMS}}`, `{{SUPPLIER_PORTAL}}`, `{{AP_RUN_DAY}}`; finance is
`{{FINANCE_CONTACT}}` (`me.md`), reached internally, never CC'd. Block 1 replies:
`procurement-payments.shape.md`, after the core payments shape's first check (is the post
logged?). A token `none` -> that step doesn't exist; TODO -> no claim about it, ⚠️.

<!-- rule:terms-from-trigger -->
**Terms count from their trigger, never from the creator's first nudge.** "Net 30 from
invoice" starts the day a complete invoice arrived (PO number on it, tax form on file);
"14 days after go-live" starts at go-live. Work the due date out from the record; a
missing piece means the clock hasn't started - say which piece, kindly and exactly.

- **Never promise a payment date.** The due date under the terms is a fact; the day money
  moves is finance's. The AP run day may be named as how finance pays approved invoices,
  never as "you'll be paid on Thursday" until finance has confirmed it.
- **The close carries the paperwork:** on an accepted deal, the steps the creator will
  meet (the PO number on the invoice, the tax form, the portal) ride in the same email,
  so the first invoice arrives complete.
- **Chase finance internally, once, with specifics** (creator, invoice date, PO, amount
  due, what's missing) - a ⚠️ line in the report. **No second holding note:** once a
  creator has had "I'm checking", the next email carries news or a named day (compass #1).
- **Payment terms asked in a negotiation** (net 15 instead of 30, upfront): the terms are
  finance's, never a lever in a draft; the core's upfront play holds (plays L).
- Creator-note field: `payment_docs: <form> on file (<date>)` - never the number itself.

## Never (this module)

- Never ask for a tax ID, SSN or bank number by email, or repeat one a creator sent.
- Never give tax advice (which form, which treaty rate): name the forms we collect.
- Never change bank or payee details from an email: Block 0, confirmed in the portal or
  through the address on file.
