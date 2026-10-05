# Contributing

Creator Management Inbox is maintained by Fluencrs (Håkon Junge and Yuliia Maryniak).
For now **pull requests are maintainer-only**, but the playbook gets better from
real-world feedback, and that's where you come in.

## Support scope

Best effort from a small team. Supported today: Gmail on macOS in Claude Code.
Linux and Windows (WSL) are less tested; Outlook is planned. No one-to-one setup
help or guaranteed response times - the most widely felt problems get fixed first.

## Ways to help

- **Report a draft that wasn't good enough** - the "Draft quality" issue template.
  This is the most valuable feedback there is. Use fictional or fully redacted
  examples: no real creator names, emails, fees or anything from a real inbox.
- **Report a bug** - the "Bug" template. Include `inbox doctor` output (it contains no
  secrets) and what you asked Claude to do.
- **Ideas, questions, show-and-tell** - [Discussions](../../discussions).
- **Security issues** - privately, via the Security tab. See [SECURITY.md](SECURITY.md).

## What makes a good playbook change

A rule belongs in the shared skills when it's true for most people running creator
partnerships, not just one company. Tell us:

1. the situation (fictional example),
2. what the draft did,
3. what an experienced partnerships manager would have done, and why.

Company-specific rules belong in your own profile (`house-rules.md`, `voice.md`),
and the workflow will offer to put them there.

## For maintainers

Before every push:

```bash
python3 -m unittest discover -s tests -v
./scripts/leak-scan.sh
```

- Keep private names that must never appear in `.leak-patterns.local` (git-ignored)
  and in the `LEAK_PATTERNS` repository secret for CI.
- Releasing: bump `version` in `plugins/creator-management-inbox/.claude-plugin/plugin.json`,
  add a `CHANGELOG.md` entry, merge to `main`. Users with auto-update get it on
  their next session; unchanged versions are not re-delivered.
- Sizes only shrink: `tests/lean_baseline.json` holds today's line, word, description
  and duplicate-text counts, and `tests/test_repo.py` fails if any grows. Fold new rules
  into existing lines rather than appending. After shrinking something, lock it in with
  `python3 tests/test_repo.py --write-baseline`.
- Never add real creator data, real emails or real rates - examples are fictional,
  figures illustrative.
