# Your rate bands

> How much a piece of creator content is worth to you, per 1,000 views (CPM).
> The rate engine turns these into an OPEN offer, a TARGET and a private MAX for
> every negotiation. Set them up with Claude: say "set up my rates". You can also
> build them from your past deals: "build my rate bands from this list of past deals".
>
> Until the block below has real numbers, money drafts won't name a fee: they ask
> the creator for their stats and flag the thread for you. That is deliberate.

## Where these numbers came from

TODO - e.g. "our last 25 paid YouTube deals, 2025-2026", or "industry surveys plus
gut feel, refresh after 10 deals". Write it down so you know how much to trust them.

## Your pricing logic in words

TODO - anything the numbers don't capture. e.g. "we pay more for tutorials than
for vlogs", "never above $3k for a first deal", "long-form converts 3x short-form for us".

## The numbers

Edit only the values. `low` / `typical` / `high` are the CPMs (price per 1,000
median views) you'd pay: `low` is a great deal, `typical` is fair, `high` is
the most you'd go. Delete formats you don't buy.

```rates
currency: TODO

# format: low=CPM typical=CPM high=CPM   (views-priced programs)
# Rate-card program? Write fees instead and add unit=fee, e.g.
#   ugc_video: low=150 typical=200 high=300 unit=fee
# Views and geo are then optional for that format.
youtube_dedicated: low=TODO typical=TODO high=TODO
youtube_integration: low=TODO typical=TODO high=TODO
youtube_short: low=TODO typical=TODO high=TODO
tiktok_video: low=TODO typical=TODO high=TODO
instagram_reel: low=TODO typical=TODO high=TODO

# Audience geography multipliers. T1 is your best market (1.0).
geo_T1: 1.0 countries=TODO
geo_T2: TODO countries=TODO
geo_T3: TODO countries=TODO

# Minimum fees. Quoting under these prices you as the cheap brand.
floor_shortform: TODO
floor_longform: TODO   # UGC: floor_ugc (or floor_<format>) - never the long-form floor

# Optional - only if you know it. What 1,000 views earn you on average, per format.
# Unlocks value-based ceilings (MAX never above what a post is worth).
# value_per_1k_views: youtube_integration=TODO tiktok_video=TODO
```
