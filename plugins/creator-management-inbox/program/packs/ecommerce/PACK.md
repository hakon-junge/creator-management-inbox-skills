# Pack: ecommerce (physical products sold online: orders and revenue)

Chosen by `business: ecommerce`. The creator gets product - a kit to keep, plus a fee for
paid work; their audience gets a discount code or a tracked link; success is orders and
revenue. Loads with the negotiation core in Block 3, and in Block 2 when content makes a
product claim (the regulated list below). Default modules: the last section.

## Success, said to a creator

- `success: sales`: "What we look at is orders from your audience - your code and your
  link are how we see them." The bar, if `deals.md` allows sharing it: orders needed at
  the fee (`conversion-bar`, with `{{CONVERSION_VALUE}}` as what one order is worth).
- Recaps: what the store recorded over `{{PAYBACK_WINDOW}}` (clicks, orders, revenue, code
  uses) from the user's data source - never estimated, never another creator's numbers.
- Never promise a sales outcome, a conversion rate or what an order will earn them.

## Attribution, in plain words

- One personal code (the note's `promo_code`) and one tracked link per creator. An order
  is theirs when the code is used at checkout or the link's visit ends in an order, as
  the store's order export shows it (the discount-code and UTM columns of a Shopify-style
  report).
- The code is the CTA that survives a repost, a screenshot or a story without a link: it
  rides in every brief and every approval, spelled exactly.
- "How do you track my sales?" -> the code, the link, where they can see results (their
  own dashboard if the program has one, else the recap) and when. Never claim every
  order is caught: other devices, direct visits and shared codes leak both ways.
- A code on a coupon site or orders that look off are the user's call: state the facts
  in the report, never an accusation in a draft.

## The offer: product, a code, and a fee for paid work

- The kit is how a creator meets the product, never the fee for a contracted post
  (`gift-as-payment`). Say concretely what's in it and which variant is theirs.
- The audience offer is `{{CREATOR_PROMO_OFFER}}`, word for word; it stacks with a
  sitewide sale only if the offer says so.
- Door A's extras (money-core): the kit (`{{CREATOR_TRIAL_GRANT}}`) and a code for their
  audience; commission per order only while the affiliate module is on.
- **Giveaways are product, never cash:** a bundle from the range, sized per money-core
  §4, shipped only where the seeding policy ships; the creator runs the giveaway, we
  ship the prize.
- **"Other brands pay more":** a bigger basket or margin pays more per post and ours can
  still be fair - our number follows what an order from this audience is worth.
- A first quote to a new creator states the payment terms in one line: `{{NET_TERMS}}`,
  and what the invoice needs (`{{PO_PROCESS}}`, `{{TAX_FORMS}}`).

## Regulated claims for physical consumer products

Per `claims-handling`, a claim on this list is Block 0 until the escalation contact has
seen it; on a live post, the draft asks for it down today, ⚠️ the same day.

- **Health and medical:** treats, cures, prevents or heals a condition (acne, eczema,
  hair loss, pain, sleep, anxiety); "dermatologist-recommended" with no source on file.
- **Cosmetic efficacy beyond experience:** a measured or permanent result ("40% fewer
  lines", "clinically proven" with no study on file), sun protection or SPF, and
  "hypoallergenic", "non-comedogenic" or "safe for sensitive skin" unless `company.md`
  states it.
- **Supplements and anything ingested:** a body-function or disease claim, weight loss,
  a dose, "safe in pregnancy".
- **Children:** a product made for children, a child using it on camera, or a safety
  claim ("safe for babies", "non-toxic").
- **Green and origin claims** ("clean", "natural", "organic", "vegan", "cruelty-free",
  "sustainable"): only as `company.md` words them; anything stronger is on the list.

Experience is fine ("my skin feels softer after a week"); a result promised to the viewer
is a claim. A claim off the list gets the draft-and-flag default.

## Seasonal peaks

- The brand's peaks are in `{{CAMPAIGN_CALENDAR}}` (a holiday gifting season, a sale
  event, a launch). Book earlier, and count back from the post date - shipping lead time,
  a draft, an approval round - before naming any date.
- Peak weeks fill creators' calendars and lift their rates: say so only when it's true;
  never invent scarcity.
- A post after its peak loses most of its value: the window decides (`budget-campaign-pot`).
- Check stock before a post pushes one variant through a peak; an "order by" date for
  holiday delivery comes only from `company.md`.

## Default modules

- `gifting-seeding` - kits, variants, addresses, ship dates, gift or deal said plainly.
- `usage-rights` (`priced`) - every right a separate priced line from `deals.md`.
- `exclusivity` - a narrow category for a set length, priced from `deals.md`.
- `budget-campaign-pot` - the campaign window and each creator's internal share of the pot.
- `affiliate` (`per-order`) - commission per order through their code or link, quoted
  from `affiliate.md`; off when it says `none`.
- `agency-talent` (`engage`) - our scope first, the agency's quote against it.
- `procurement-payments` - net terms, PO numbers, tax forms, the supplier portal.
