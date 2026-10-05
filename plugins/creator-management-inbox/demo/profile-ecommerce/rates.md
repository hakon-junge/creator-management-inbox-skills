# Your rate bands (DEMO - fictional numbers)

## Where these numbers came from

Quillmoss's (fictional) last 34 paid bookings across four campaigns, 2025-2026, plus
the UGC rate card we've used since January 2026. Refresh after Holiday Glow.

## Your pricing logic in words

Fee bands per piece, not views: a creator or agency quotes, and we read the quote
against the band. The bands fit creators with roughly 15k-150k median views whose
audience is mostly in the US, UK or EU; a bigger creator, or anything above the
3,000 USD sign-off limit for one creator in one campaign, needs sign-off. Paid usage,
raw files and exclusivity are never inside these fees - they are priced on top from
the tables in `deals.md`. UGC is our rate card: we name the per-video fee ourselves.

```rates
currency: USD

# Fee per piece (unit=fee): views and geo are optional for these formats.
tiktok_video: low=700 typical=1100 high=1600 unit=fee
instagram_reel: low=650 typical=1000 high=1500 unit=fee
instagram_story_set: low=250 typical=380 high=520 unit=fee
youtube_integration: low=1200 typical=1800 high=2600 unit=fee
ugc_video: low=260 typical=330 high=420 unit=fee

# Where the audience is. We only ship to these countries.
geo_T1: 1.0 countries=US
geo_T2: 0.9 countries=UK,IE
geo_T3: 0.8 countries=rest of the EU

# Minimum fees. (ugc_video counts as long-form here: 250 is the UGC floor.)
floor_shortform: 250
floor_longform: 250
```
