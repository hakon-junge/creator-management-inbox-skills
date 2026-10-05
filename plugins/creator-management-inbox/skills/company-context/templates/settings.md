# Settings

Change a value after the colon and save. Lines starting with `#` are notes.
Ask Claude "change my inbox settings" if you'd rather not edit this by hand.

```settings
# Where drafts go: gmail = your real mailbox (drafts only, never sends), demo =
#   fictional creator emails saved as files you can open (demo_profile: saas or ecommerce)
provider: demo
demo_profile: saas

# House style, applied to every draft automatically.
#   em_dashes: replace (swap em dashes for a spaced hyphen) or allow
em_dashes: replace
#   banned_words: word=replacement pairs, comma separated. Blank = none.
#   Example: honest=straight, honestly=genuinely
banned_words:
#   exclamation_marks: allow, or avoid (warns you when a draft has one)
exclamation_marks: allow

# Run log - how the workflow learns from what you actually send.
#   learn    = keep draft text for run_log_days, then delete it (recommended)
#   metadata = keep only a fingerprint of each draft (no text)
#   off      = keep nothing (no zero-edit score, no learning)
run_log: learn
run_log_days: 14

# Your own link domains, comma separated (website, tracking links, shortener).
# Only links on these domains are ever looked up online.
link_domains:

# Teammates who may be CC'd on drafts even if they aren't on the thread.
team_addresses:

# Most unread threads handled in one run.
max_threads: 50
```
