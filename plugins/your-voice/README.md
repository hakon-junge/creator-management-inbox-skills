# Your Voice

**Everything Claude writes for you, in your voice.** Emails, replies, chat messages,
LinkedIn posts, docs.

- **Good from minute one.** Until you build your own, Claude writes in a default
  voice: direct, warm and clean. The point first, one clear ask, nothing said twice,
  no em dashes, no "I hope this email finds you well".
- **Learns you in a few minutes.** Say "build my voice". Claude reads your sent
  writing (only messages you actually wrote), measures your habits, writes your
  voice profile and shows you three sample rewrites. You confirm or correct; no long
  interview.
- **Keeps up with you.** Say "refresh my voice" (Claude suggests it monthly). Small
  wording changes it has seen several times are applied; anything that changes how
  you handle things is asked first.
- **Yours to take anywhere.** One plain `voice.md`. Edit it by hand, or paste it into
  any other AI tool.

## Install

Claude Code or Cowork:

```
/plugin marketplace add hakon-junge/creator-management-inbox-skills
```

```
/plugin install your-voice@creator-management-inbox-skills
```

Claude.ai: zip the `skills/your-voice` and `skills/your-voice-builder` folders and
upload each one as a skill. Without a terminal, Claude gives you the finished
`voice.md` to save as a project file.

## Use it

| Say | What happens |
|---|---|
| `write a reply to this in my voice` | Drafted in your voice (or the default voice until you build yours) |
| `build my voice` | Reads your sent writing, writes your voice profile, shows sample rewrites |
| `refresh my voice` | Re-reads what you wrote since the last refresh and updates the profile |
| `import my voice` | Copies a filled Creator Management Inbox voice profile, once |

Sources it can learn from: a connected Gmail or Outlook (sent mail, last 180 days),
or files you drop in `~/.claude/voice/samples/`: `.mbox`, `.eml`, `.txt`/`.md`,
LinkedIn's `Shares.csv`, a Slack export. Or paste a few messages into the chat.

## Where your voice lives

```
~/.claude/voice/          readable only by you (override with $VOICE_HOME)
  voice.md                your voice profile, plain Markdown
  samples/                exports you drop in; never copied anywhere else
  history.md              one line per refresh change
```

It sits outside the plugin, so updates never touch it. Nothing is uploaded by this
plugin: the helper script has no network access. To write in your voice Claude reads
your samples, so that text is processed by Anthropic's Claude models under your
Claude account's terms.

Licensed [MIT](../../LICENSE). Maintained by Fluencrs.
