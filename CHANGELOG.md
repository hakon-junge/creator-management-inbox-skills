# Changelog

Versions follow each plugin's `.claude-plugin/plugin.json`
(`plugins/creator-management-inbox/`, `plugins/your-voice/`). Users with auto-update
on receive a release when that version changes.

## Creator Management Inbox 1.0.0 - 2026-10-05

First public release.

- **Inbox auto-draft workflow.** Reads unread email, sorts each thread by stakes
  (admin, content, money, flagged for you), drafts the reply in your voice, threads
  it in Gmail and leaves the original unread. Ends with a one-page report. Nothing
  is ever sent.
- **Skills:** inbox-setup, inbox-auto-draft-workflow, negotiation-playbook,
  rate-engine, content-reviewer, creator-notes, company-context, comms-style and
  voice-builder.
- **Program setup.** `program.md` describes how your program runs (business type,
  model, budget, success metric, pricing method, deal shape, creator types).
  `inbox program` validates it and loads only the packs and modules your program
  switches on: the `saas` and `ecommerce` packs, and modules for affiliate, views
  pricing, budgets, usage rights, exclusivity, agencies, gifting and seeding, UGC,
  and procurement and payments.
- **Rate engine.** OPEN, TARGET and a private MAX for every negotiation from your
  own rate bands, set up by interview or built from your past deals. Supports
  per-view and flat-fee bands, geo tiers, budgets and campaign pots.
- **The `inbox` command.** Gmail read and drafts, a demo mailbox, rate cards,
  creator lookup, link unwrapping, a run log, the zero-edit score and `inbox doctor`.
- **Two demos, no mailbox needed.** `saas` (six emails to a fictional app) and
  `ecommerce` (eight emails to a fictional skincare brand). Pick one with
  `demo_profile` in settings.md.
- **Draft checks in code.** `inbox draft` refuses recipients who are not on the
  thread or in `team_addresses`, attachments from outside the attachments folder,
  hidden text and scripts, tracking-wrapped links, leftover placeholders, a private
  MAX, a total above your sign-off limit without a `[DO FIRST: ...]` line, and a
  claim that something is done when it is not.
- **Send guard.** A hook that blocks reading the Gmail token, send calls and mail
  connector actions, and during a run also blocks acting connector tools, web
  fetches, shell network clients and changes to `settings.md` and `me.md`. It is a
  deny-list, one layer of four: see [SECURITY.md](SECURITY.md).
- **Privacy.** Gmail permissions narrowed to readonly and compose, your own OAuth
  app, owner-only files in one private folder, pinned dependencies, and a warning
  when that folder sits inside a cloud-synced folder.
- **Self-tuning.** Each run compares its drafts with what you sent and proposes
  rules from your edits.

## Your Voice 1.0.0 - 2026-10-05

First public release.

- **`your-voice` skill.** Writes email, chat, LinkedIn posts and docs in your voice,
  picks the register by channel, applies your house style before handing text over
  and suggests a refresh after 30 days.
- **A default voice** (direct, warm, clean) used until you build your own, and
  `voice-template.md`, the structure every voice.md follows.
- **`your-voice-builder` skill.** Builds voice.md from your sent mail (Gmail or
  Outlook connector), exports or pasted text. Confirms with a summary and three
  sample rewrites. Refresh mode applies well-evidenced wording changes and asks
  about anything that changes a rule. One-time import of a Creator Management Inbox
  voice.
- **`voice.py`** (standard library, no network): `init`, `where`, `import` (.txt,
  .md, .eml, .mbox, LinkedIn Shares.csv, Slack export, connector JSON), `stats`,
  `check` and `clean`. Mail counts only when the parsed sender address matches
  exactly; quotes, forwards and signatures are stripped.
- **Private voice home** `~/.claude/voice/` (`$VOICE_HOME`): directories 0700,
  files 0600.
