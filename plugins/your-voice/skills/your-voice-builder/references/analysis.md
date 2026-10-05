# Reading samples into a voice

Turning someone's own messages into a voice.md that makes drafts sound like them:
count first, then read like an editor, then write only what the evidence supports.

## 1. Start from the numbers

Run `voice.py stats` and use its numbers for every frequency you write. Never
estimate what you can count. Translate shares into plain words:

| share | write |
|---|---|
| 0 | "never" (say how many samples: "in 40 emails") |
| 0.01-0.15 | "rarely, about 1 in 10" |
| 0.15-0.35 | "about 1 in 4" or "1 in 3" |
| 0.35-0.65 | "about half the time" |
| 0.65-0.90 | "usually" |
| 0.90+ | "almost always" |

With fewer than 10 samples in a channel, write "in [N] messages" rather than a
rate, and make no fine-grained claims about that channel.

Per channel: `median_words`, `median_sentence_words`, `median_paragraphs`,
`greetings`, `openers`, `closers`, `share_typed_name`, emoji and `top_emoji`,
exclamation marks, smileys, `em_dashes` vs `spaced_hyphens`, bullets, and
`recurring_phrases` (the shortlist for Phrases).

## 2. Read like an editor

Sort the samples by situation before reading: first contact, reply, quick answer,
an ask, good news, feedback on someone's work, a decline, a number or negotiation,
a nudge, an internal update, a post. Read at least two or three of each situation
that exists. For each, note:

- how it opens (the first line, and whether there's a greeting at all)
- where the point lands (first line? third paragraph?)
- how the ask is phrased, and whether it has an exit
- how it closes, and whether they type their name
- what they could have done and didn't (no apology, no recap, no emoji)

## 3. Evidence rules

- **A trait needs 3+ samples** showing it, from different threads or recipients.
  Three messages in one thread count as one.
- **A phrase needs 2+ separate samples.** Confirm each `recurring_phrases` entry by
  reading where it occurs: a quoted line or a pasted template is not voice.
- **A register needs 5+ samples in that channel.** Fewer: mark it `(default)` and
  let the default voice cover it.
- **Moods are not voice.** One rushed reply or one formal letter doesn't make a trait.
- **Contradictions are information.** Record both sides with the condition: "Warm
  and a little longer with new contacts; two lines with long-time partners."
- **Absence is evidence.** If the default voice would do something and they never
  do it across 20+ samples, it belongs in Never or in Formatting.
- **Their words, not yours.** Don't polish their phrasing into better copy. The goal
  is recognisable, not impressive.

## 4. Writing each section

**Core voice.** 4-7 traits. Each: the trait in bold, why it works, a short example
in their words.
- Weak: "Friendly and professional." (true of everyone, so useless)
- Strong: "**Warm through specifics, not adjectives.** Names one concrete thing the
  other person did, which makes the praise believable. 'The way you used the empty
  calendar as the hook was clever.'"

**Openers and greetings / Closers.** By situation, with frequencies: "Hi [Name], in
about 9 emails in 10; no greeting mid-thread." Note `share_typed_name`.

**Registers.** Only channels with enough samples. Describe length, structure and
what changes from email: "Chat: one to three lines, no greeting, decisions as
numbered options with a pick."

**Shapes.** From their real messages in each situation, the order of moves, not the
words: "Declines: thanks, the reason (always timing or fit), what would change the
answer, nothing else."

**Formatting.** From the stats: paragraph length, bullets, dashes, emoji (which ones,
where, how often), exclamation marks, smileys, links, P.S. lines.

**Phrases.** 5-15, quoted exactly after redaction, each seen in 2+ samples. Prefer
distinctive over generic: "let me know" earns a place only if it's their dominant
closer.

**Never.** What they avoid where others wouldn't, and anything they rejected when
confirming. Keep the default voice's never-items unless their samples contradict
one (if they often open with "Hope you're well", it's theirs, not a never).

**House style.** Derive the block from the numbers:
- `em_dashes`: `replace` unless they use em dashes in at least 1 message in 5; then
  `allow`, and say so in the summary so they can choose.
- `exclamation_marks`: `avoid` if under 1 message in 10 has one, else `allow`.
- `emoji`: `never` at 0, `rare` up to about 1 message in 5, `free` above. Use the
  email numbers when there are any; describe other channels in Formatting.
- `banned_words`: keep the default's honest-frame pairs unless they say "to be
  honest" often (then ask). Add only words the user names.

## 5. Redaction (before anything is quoted)

- Other people's names -> [Name]. Other companies -> [Company]. Prices, figures,
  dates -> [amount] / [date]. Links -> [link].
- Leave out anything personal or confidential: health, family, money of named
  people, anything marked confidential, internal disagreements.
- Only the user's own sentences. If a quoted reply slipped past the import, skip it.

## 6. Size

Under about 1,200 words. When over, cut in this order: the weakest examples,
overlapping traits, shapes they rarely need, phrases beyond 12. Never cut the house
style block or the never-list.

## 7. The confirm step

A 6-8 line summary, in plain words, with numbers:

> From 48 emails and 12 LinkedIn posts:
> - You get to the point in the first line; almost no warm-up.
> - "Hi [Name]," in about 9 emails in 10; no greeting mid-thread.
> - You give the reason with every no, and never apologise for a number.
> - About 1 email in 4 ends with an emoji, never one to a client.
> - Posts open on a moment and end on a question.
> - Never: "circle back", em dashes, a typed name at the end.

Then three short rewrites in the new voice: a quick reply, a decline, and a message
with a number in it. Use neutral, invented situations unless the user offers real
ones. Ask: "Anything wrong?"

## 8. Refresh: what changed?

Compare the new stats and samples with what voice.md says.
- **New phrase, opener or closer:** in 3+ new samples from different threads and not
  in voice.md -> add it (auto).
- **Phrase dropped:** listed in voice.md, unused in 15+ new samples of that channel
  -> remove it or mark it rarer (auto).
- **Frequency moved:** a share differs from voice.md's by 0.15 or more, with 10+ new
  samples in that channel -> update the number (auto).
- **Length moved:** median words differs by 30% or more, with 10+ new samples ->
  update it (auto).
- **Ask instead:** anything that changes a stance or rule (now proposes calls, now
  uses emoji with clients, a new never-item), anything seen fewer than 3 times, and
  any change to the house-style block.
