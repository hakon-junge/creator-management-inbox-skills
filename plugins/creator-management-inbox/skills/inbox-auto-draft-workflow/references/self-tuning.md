# Self-tuning - learning from what the user actually sends

Loaded at Step 0 of a run when `inbox score` has drafts to compare, and when the user
asks how drafts are doing.

`inbox score` (Step 0) compares each draft as saved with what the user really sent on
that thread (exact, bar whitespace and quote marks). It reports `zero_edit` per thread,
`similarity` and the rate: "X/Y sent unedited - Z%". Target a sustained 90%+: a draft rewritten before sending saved no
one anything.

For edited drafts (`run_log: learn` keeps the text for 14 days), look at the
material deltas - a cut clause, an added fact, a reworded ask - and turn each into
a one-line candidate rule. A draft sent unedited on a thread that then died (no
reply, no commit, no go-live) is a caution flag, not a win: where it died points at
the step to rework. Where a rule belongs:

- **wording** (a phrase they always change, an opener they cut) -> `voice.md`, via
  `voice-builder`
- **a decision** (they always add the brief link, never mention X) ->
  `house-rules.md` in their profile folder (create it if missing)
- **a fact** (a term changed) -> the right profile file

A candidate seen twice is proposed to the user; apply it only when they agree.

**Anti-bloat guard.** Fold a rule into an existing line wherever possible; never
append dated case notes. Keep `house-rules.md` under ~600 words and `voice.md`
under ~1,200. An always-on file that grows by one plausible sentence a week is
the reason a voice goes generic.

Rules that would help everyone belong upstream: suggest the user opens an issue
on the repo (see CONTRIBUTING.md) - never edit the plugin's own files.
