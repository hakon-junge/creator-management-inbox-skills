---
name: <your name>
built: <YYYY-MM-DD>
refreshed: <YYYY-MM-DD>
sources: <e.g. gmail sent 180d (42 emails), linkedin export (18 posts)>
samples: <number of samples read>
---

# Voice: <your name>

> One or two plain sentences: how this person sounds and what they never sound like.
> Built by "build my voice". Kept under about 1,200 words: tight beats complete.

## Core voice

4-7 traits. Each is one bullet: **the trait.** The reason it works. A short example in
their own words, with other people's names as [Name] and figures as [amount].

## Openers and greetings

By situation: first message to someone new, a reply, a quick mid-thread answer, a
message to a group. Note when they skip the greeting. Real examples.

## Closers

By situation: after an ask, after good news, after a no, in a quick reply. Whether
they type their name or let the signature carry it.

## Registers

Only the channels their samples show. Mark any other channel `(default)` and inherit
it from the default voice.

- **Email:** length, structure, how the point and the ask are placed.
- **Chat:** length, line breaks, how decisions and requests are framed.
- **LinkedIn:** how posts open, build and end.
- **Docs:** how they structure plans, notes and updates.

## Shapes

How they handle the moments that matter, 2-4 lines each, as principles: a first reply
to an interested contact, feedback on someone's work, a decline, a number or a
negotiation, a nudge or follow-up.

## Formatting

Paragraph length, bullets, bold, dashes, links, P.S. lines. Emoji and exclamation marks
as frequencies from `voice.py stats` ("about 1 email in 4 has one, always at the end").

## Phrases

5-15 lines they really use, quoted. Only phrases seen in 2+ separate samples.

## Never

Words, openers, closers and habits they avoid or have rejected, each with the swap
where one exists.

## House style

Enforced on every text before it is handed over. Change values here, nowhere else.

```house-style
em_dashes: replace
banned_words: to be honest=to be direct, I'll be honest=I'll be direct
exclamation_marks: allow
emoji: rare
```

- `em_dashes`: replace (spaced hyphen instead) or allow
- `banned_words`: word=replacement pairs, comma separated (empty replacement = remove)
- `exclamation_marks`: allow or avoid
- `emoji`: never, rare (one at most) or free
