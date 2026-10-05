# Set up rates ("set up my rates", about 10 minutes)

Loaded from `rate-engine` only for this job, never in a drafting run.

Rates live in the user's `rates.md` (`inbox profile-dir` shows the folder). Two
ways in - offer both:

**A. From past deals (best, if they have 5+).** Ask for a list or spreadsheet export
with format, fee and views (median views of the post, or the views it got). Save it
as a CSV with the header `format,fee,views` in the scratchpad, then:

```bash
inbox rate-bands --csv <file>
```

It returns low / typical / high CPM per format (25th / 50th / 75th percentile) and
flags formats with too few deals. Show the table and sanity-check it with them: "Does
paying 25 per thousand views for an integration feel like your normal?"

**B. Guided interview (no history, or to fill gaps).** Ask in small batches:

1. "Which formats do you pay for?" (list them in `rates.md` terms)
2. For each: "For a creator with about 20,000 views, what would feel like a great
   deal, a fair price, and the most you'd ever pay?" Convert to CPM: fee / views x 1000.
3. "Which countries are your best customers in? Where do viewers convert less?"
   -> T1 / T2 / T3 and multipliers (T1 = 1.0; ask how much less a T2 viewer is worth,
   typical answers 0.5-0.8).
4. "What's the smallest fee you'd offer for a short video? A long one?" -> floors.
5. Optional: "Roughly what is 1,000 views worth to you in revenue?" Help them estimate:
   customers per 1,000 views x value of a customer (`deals.md`). Skip if unknown.
6. "Any rules the numbers don't capture?" -> "Your pricing logic in words".

Write the ```rates block, fill "Where these numbers came from" honestly ("gut feel
plus 3 deals, refresh after 10"), and run one test quote with them on a creator
they know, to check it feels right.

**No numbers at all yet?** That's fine. Negotiate from published third-party rate
surveys, say so internally, treat the first deals as benchmark-setting (more
creators at smaller fees), hold floors from day one, and build real bands from the
first 8-10 deals with `inbox rate-bands`.
