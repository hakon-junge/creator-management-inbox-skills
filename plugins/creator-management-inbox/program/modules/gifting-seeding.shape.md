# Module shape: gifting-seeding (Block 1 replies)

Loads in Block 1 with `gifting-seeding.md` when product is about to ship or has shipped.
Reads: `{{SEEDING_POLICY}}`, `{{SEEDING_FORM_URL}}`, the products and variants in
`company.md`, `{{CURRENT_CAMPAIGN}}`, the note's `gifts_sent`. **Every ship date we give**
(a first kit, a replacement, a restock) is the policy's lead time counted from the form
plus its transit time to their country, in one sentence ("ships within two working days
of the form, then 4-6 days to you").

## The first seeding email (a yes to a kit)

1. Warm and specific: what's coming, and why them (their audience, a routine they showed).
2. **The line that prevents every later argument:** no strings, or an expected post, in
   one plain sentence (`gift-as-payment`).
3. Disclosure either way: if they post it, it's marked #gifted (#ad on a deal) - said
   once, lightly, as standard practice, never as suspicion.
4. Their variant: two or three named options from `company.md`, or the one the brief
   fixes - never an open "which one do you want?".
5. The address: the seeding form link, bold and hyperlinked; never "reply with your address".
6. When it ships: lead time plus transit (every ship date, above).

## Addresses

Collected only through the form. One that arrives by email is never repeated back, quoted
or copied into the note: thank them without restating it; the report carries "enter the
address from the thread via the seeding form" as a pre-send action.

## "Where's my package?"

- A tracking number or link in the thread or the shipping record -> paste it with the
  carrier's estimate.
- None on record -> `[DO FIRST: paste the tracking link]` and nothing that says it shipped
  (`done-claims`); past the lead time with no tracking -> the honest state, a named day
  for the next update, ⚠️ so the user chases the warehouse.

## Out of stock, a wrong variant, damaged

- Two concrete alternatives, never "we'll sort something out": the nearest variant,
  another product from the range, or the same one on a restock date that `company.md` or
  the thread states.
- Wrong, missing or damaged: a replacement through the form (ship date as above); keep or
  return the first one per the policy.
- A post tied to that variant moves with it: re-date it in the same reply (scheduling).

## A region the policy doesn't ship to

A warm decline plus a non-physical alternative if a real one exists - their code for
their audience, a digital asset, the next seeding when shipping opens (only if planned).
Never a forwarding address or a one-off exception: customs, duties and returns would land
on the creator.

## After the kit lands

- An expected post: one check-in after the agreed date (`follow-up-ladder`); late
  against a contracted date -> `shapes/late-deliverables`.
- They posted unprompted -> thank them and log it in `gifts_sent`; reposting it on our
  channels is a usage right - ask before reposting.
- Cash on top -> Block 3 (`gift-as-payment`).
- Duties or customs fees: who pays per the policy; never promise there won't be any.
