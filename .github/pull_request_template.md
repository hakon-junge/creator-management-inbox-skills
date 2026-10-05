<!--
Pull requests are maintainer-only for now (see CONTRIBUTING.md). Not a maintainer?
Please open an issue instead: the "Draft quality" or "Bug" template.
-->

## What this changes

<!-- One or two sentences: what is different after this merges, and why. -->

## How it was checked

<!-- What you ran or tried, and what you saw. -->

## Checklist

- [ ] Tests pass: `python3 -m unittest discover -s tests`
- [ ] Leak scan passes: `./scripts/leak-scan.sh`
- [ ] Examples are fictional: no real creator names, emails, fees or anything from a real inbox
- [ ] Nothing grew past its budget (`tests/lean_baseline.json`): new rules are folded into existing lines
- [ ] If this touches the guard hook, the draft checks or Gmail permissions: the description says what is now allowed or blocked, and `SECURITY.md` still matches
- [ ] If users should receive this: `version` is bumped in `plugin.json` and `CHANGELOG.md` has an entry
