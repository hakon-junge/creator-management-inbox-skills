# Working on this repo

This repo IS the creator-management-inbox plugin. Users install it; don't treat it as a
place to run their inbox.

- Skills: `plugins/creator-management-inbox/skills/`. Method only - facts come from the
  user's profile (`company-context` + templates). Never add real company, creator or
  rate data; examples are fictional.
- The `inbox` CLI: `plugins/creator-management-inbox/scripts/` (stdlib + Google client libs).
  No send command, ever.
- Before committing: `python3 -m unittest discover -s tests -v` and
  `./scripts/leak-scan.sh`. Both must pass.
- Sizes are ratcheted by tests against `tests/lean_baseline.json`: nothing may grow.
  Fold, don't append. Shrank something? `python3 tests/test_repo.py --write-baseline`.
- A user-visible change needs a version bump in `.claude-plugin/plugin.json` and a
  CHANGELOG entry, or auto-updating users won't receive it.
- A second plugin, Your Voice, lives in `plugins/your-voice/`: its own version, Python
  stdlib only, no hooks, no `bin/`, fictional examples. Tests: `tests/test_voice.py`.
  Its default voice must stay free of names, brands and catchphrases (test-enforced).
