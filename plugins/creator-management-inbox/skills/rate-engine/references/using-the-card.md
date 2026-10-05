**Load when:** a money thread puts a fee in play (Block 3 base). The full `rate-engine`
skill loads only to set up rates, for warehouse benchmarks or for bulk pricing.

# Using the rate card in a draft

```bash
inbox rate --format youtube_integration --views 41000 --tier T1 --ask 2400
inbox rate --format tiktok_video --views 90000 --tier blend --proven --renewal
inbox rate --format ugc_video --ask 350        # fee bands (unit=fee): views and geo optional
```

Formats come from `rates.md`. `--tier` (required with 2+ tiers) is the **audience's**
geography, not the creator's; unknown -> ask for their stats, or `blend` (the tiers'
average). `--proven` = good results on record (MAX may reach the post's full value).
`--budget N` (and a campaign pot's per-creator share) caps OPEN / TARGET / MAX; `--renewal`
and `--views-kind median` word the basis. For 24 h `inbox draft` refuses a printed MAX.
**Rates not set up** (`rates.md` missing or `TODO`) -> the command refuses with "advisory":
no fee in the draft; ask for their current stats, say a proposal follows, ⚠️ "set up
rates". A guessed rate card gets quoted, anchors the creator and can't be un-sent.

| Field | Meaning | Creator-facing? |
|---|---|---|
| `open` | where you open | yes, with its mechanism |
| `target` | where you want to land | yes, as a later step |
| `max_private` | walk-away ceiling | **never** |
| `ladder` | open -> two shrinking steps -> target | the steps, one per round |
| `verdict` | `NEGOTIATE`, or a no-flat-fee verdict (MAX under the floor, or `DECLINE-BY-MATH`) | no - it routes the move |
| `ask.read` | where their ask sits against OPEN / TARGET / MAX (value-capped, not the raw market band) | no - it tells you how hard to push |
| `ask.x_max` | their ask / MAX | no - it picks the play (playbook `above-band`) |
| `basis_sentence` | a starting point for explaining the number | adapt it in their voice |

OPEN = the low end of the band, TARGET = typical, MAX = the high end; how the band (and any
value cap on it) is computed is the pricing module's, a rate card uses its fee range itself.

- **Policy floors win.** `floor_shortform` / `floor_longform` protect the relationship,
  not the budget: a quote under the floor prices you as the cheap brand for every future
  conversation. MAX under the floor = the post is too small for a flat fee: a no-flat-fee
  verdict, and the active modules' no-fee path, never a flat-fee counter.
- **DECLINE-BY-MATH** = even the cheap end of the market exceeds what the post is worth;
  common in low-value-per-view niches even when the ask looks "within band".
- **Precise numbers.** The ladder rounds to figures like 1,240, not 1,250 (never under the
  floor): precise reads as calculated, round as invented, inviting a round counter.
- <!-- rule:conversion-bar -->
  **The creator-facing conversion bar** (optional, only if `deals.md` allows it):
  `fee / (value per customer x 0.5)` = the number of customers at which the deal clears at
  TARGET (value per customer = `{{CONVERSION_VALUE}}` in `deals.md`; 900 at 45 per customer
  -> 40). Always the TARGET basis, never MAX or full value: a bar at the walk-away is one
  the creator clears while the deal still loses money. Compute it at both the target fee
  and the creator's current fee (the advanced engine prints `conv_bar_target` /
  `conv_bar_current`). It is a performance expectation, not a valuation of their audience,
  and the only internal-economics figure that may cross to a creator.

## The number in the draft

- **Data before number.** The inputs the pricing module names, from the creator's note or
  the thread first; only ask the creator when they're missing or older than ~6 months, and
  then for a screen recording of their analytics, not screenshots.
- **Quote in `{{CURRENCY}}` and be explicit about tax** (gross or net, per `deals.md`). An
  ambiguous figure means someone eats the tax later.
- **MAX is internal only.** A counter at or below MAX from a converting creator is
  effectively a yes.
- **Per-post results are hit-driven.** Only some posts win even when priced right; the
  portfolio is what's profitable. Never promise a per-post outcome, and never reprice off
  one dead post.
- **Unproven formats aren't a default paid line.** A format with no band rides as a
  bundled, clearly-flagged test inside an agreed total.
- **Log what you actually paid versus the band.** Every override, in the creator's note:
  the next rates setup either vindicates the override or ends it.
