# How you do deals with creators (DEMO - fictional)

## What you buy

- Formats you pay for: TikTok videos, Instagram Reels, Instagram story sets (3 frames
  with a link sticker), the odd YouTube integration, and UGC videos for our own ads
- `{{MIN_PIECES_FIRST_DEAL}}`: 1 - a first booking is one post (plus a story set if the
  campaign brief asks for one); creators whose codes sell get 2-3 posts next campaign
- `{{TRACK_GATE_MEDIAN_VIEWS}}`: 10000 - below it we gift a PR box and invite the creator
  to Quillmoss Collabs (`affiliate.md`) instead of paying a fee
- `{{CASH_FLOOR_FIRST_DEAL}}`: 250 USD

## Paying creators

- `{{PAYOUT_VENDOR}}`: our Accounts Payable team, by bank transfer (ACH in the US,
  international wire elsewhere).
- `{{SUPPLIER_PORTAL}}`: the **Quillmoss Supplier Hub** (https://hub.quillmoss.example),
  where creators register, upload their tax form and invoice.
- `{{NET_TERMS}}`: **net-30 from the day AP receives a valid invoice.** Valid means:
  - `{{PO_PROCESS}}`: the **PO number** from the booking confirmation is on the invoice (format
    `PO-QM-26-0000`). AP returns an invoice without one unpaid, with an automatic
    notice to the address it came from, and the 30 days never start;
  - `{{TAX_FORMS}}`: the tax form is on file in the Supplier Hub before the first payment: **W-9** for
    US creators, **W-8BEN** for non-US individuals (W-8BEN-E for a company);
  - the post is live and was approved.
- `{{AP_RUN_DAY}}`: AP pays in a weekly run every Thursday.
- `{{PAYMENT_SPEED_CLAIM}}`: net-30 from a valid invoice (PO number on it, tax form on file)
- Gross or net of tax: agreed fees are net of VAT - a VAT-registered UK or EU creator
  adds VAT on top on the invoice. No US withholding with a valid W-8BEN.
- Upfront payment: never, for anyone.
- Off-cycle payment: AP can add a corrected invoice to the next Thursday run when a
  paperwork miss held up a post that has been live 30+ days. Ask AP first
  (`{{FINANCE_CONTACT}}`); a draft may say we've asked, never that it's agreed.
- **Payment details change only in the Supplier Hub, by the creator, and AP confirms
  every change by calling the phone number already on file.** We never take bank
  details, a new payee or a new invoicing address by email - not from the creator, not
  from a manager.

## Usage rights and boosting (paid ads on creator content)

- `{{BOOSTING_TERMS}}`: Organic reposting of the post on our own channels (Instagram,
  TikTok, website, email) with credit is included in every fee. Paid usage - our ads
  using their content, or a Spark Ads / partnership-ad code from their handle - is never
  included: it is its own line from the table below, 365 days at most. A Spark or
  partnership-ad code covers the window bought and its expiry is set to the last day
  of that window; we ask for the code 7 days before the flight. Ceiling: the approved
  post only, trimmed to 15s / 30s / full length, no re-edits or new voiceover, spend
  capped at 5,000 USD per post per 30 days without the creator's OK.

`{{USAGE_RIGHTS_RATES}}`:

| Right | Influencer post | UGC video |
|---|---|---|
| Organic repost on our channels, with credit | included | included (it's made for us) |
| Paid usage, 30 days | +20% of the base fee | included |
| Paid usage, 90 days | +40% of the base fee | +30% of the per-video fee |
| Paid usage, 365 days | +80% of the base fee (sign-off) | +60% of the per-video fee |
| Spark / partnership-ad code | included with any paid window; expires with it | n/a - UGC runs from our ad accounts |
| Raw files (unedited clips) | +25% of the base fee | +15% of the per-video fee |

## Exclusivity

We buy exclusivity only when we ask for it. One-off campaign bookings, gifting and UGC
carry **none**, and we don't pay for an exclusivity clause a creator or agency adds
on their own. When we do ask (multi-campaign deals), it is priced like this, from
go-live (`{{EXCLUSIVITY_RATES}}`):

| Category | Length | Price |
|---|---|---|
| Skincare (serums, cleansers, moisturisers) | 30 days | +10% of the base fee |
| Skincare and SPF / tinted SPF | 60 days | +20% of the base fee |
| Skincare and SPF / tinted SPF | 90 days (the most we buy) | +30% of the base fee |

Never "all beauty" or "all brands". A creator's exclusivity with another brand is
theirs: note the end date in their creator note.

## Cancellations, late posts and posts that skip approval

`{{CANCELLATION_TERMS}}`, plus late posts and approval:

- **We cancel a booked post (kill fee):** nothing before the creator accepts the brief;
  50% of the base fee once the brief is accepted; 100% once the draft is approved. The
  product is theirs to keep.
- **The creator cancels, for any reason:** no fee is due to them and nothing is owed
  to us. The kill fee only ever runs from us to the creator; we never charge a
  creator, ask for product back or ask for a refund. We offer once to move the booking
  to the next campaign at the same fee.
- **Late posts:** the go-live date in the booking confirmation is the date. A new date
  must sit inside the campaign window, because codes and paid flights end with it. If
  it can't, we move the booking once to the next campaign at the same fee, or cancel
  it with nothing owed either way. A second slip moves the creator to `status: watch`.
- **Approval:** the draft goes to us by link at least 3 business days before go-live;
  we answer within 1 business day.
- **A post that skipped approval or breaks the claims or disclosure rules** (`company.md`)
  is corrected within 24 hours - a spoken claim means taking the video down and
  re-uploading an approved cut. We pay once the corrected post is live and approved.

## Seeding (gifting)

`{{SEEDING_POLICY}}`:

- **What's gifted:** the campaign PR box - for Barrier Reset, the Dew Barrier Serum
  30 ml, the Cloudmilk Cleanser 150 ml and Veil Skin Tint SPF 30 in the **two shades
  the creator picks on the seeding form**. Booked creators get a filming kit instead
  (full sizes, including the 50 ml serum). UGC creators get the product they film.
- **No strings.** A PR box never comes with an expected post, a date or a content ask.
  If they post, they label it as gifted (`company.md`).
- **Addresses only through the seeding form**, `{{SEEDING_FORM_URL}}`: https://quillmoss.example/pages/creator-seeding.
  It writes straight into Shopify. We never ask for, accept or copy an address from an
  email or a DM; an address sent by email gets pointed to the form.
- **Replacements:** a missing or damaged item -> the form's "missing or damaged item"
  option; it ships within 2 business days. One shade exchange per box within 30 days,
  also through the form. **No size swaps**: PR boxes carry the 30 ml serum only. Gifted
  product is never sent back.

## Measuring success

- `{{CONVERSION_VALUE}}`: about 58 USD contribution per first order (internal only)
- `{{PAYBACK_WINDOW}}`: the campaign window for campaign codes (they expire with it); 90 days for always-on links
- What counts as a win: orders through the creator's code or link (Shopify)
- May you tell a creator their conversion bar: no - we share their order count after the campaign, not a target

## The deal process

- After a creator says yes: the booking confirmation email (deliverables, go-live
  date, fee, PO number, usage, approval date), then the creator agreement and Supplier
  Hub registration (tax form and bank details) before the first invoice
- Contract: the Quillmoss creator agreement (two pages plus the usage schedule above)
- `{{ONBOARDING_FORM_URL}}`: see `me.md`

## Giveaways and freebies

- What you can give without cash: the PR box; up to 3 Barrier Reset Kits for a
  creator's giveaway (winners in the US, UK or EU, shipped through the seeding form)
- Giveaways always need sign-off before sending.
