# How it works

This is the detailed tour: what happens when you say "run my inbox", which skill
does what, and why it's built this way.

## The pieces

```mermaid
flowchart TB
  subgraph You["On your computer (~/.claude/inbox, private)"]
    P[profile/: company, deals, rates, affiliate, voice, settings]
    N[creators/: one note per creator]
    T[token.json: your Gmail grant]
  end
  subgraph Plugin["The plugin (updates automatically)"]
    W[inbox-auto-draft-workflow<br/>the orchestrator]
    CS[comms-style<br/>your voice applied]
    NP[negotiation-playbook]
    RE[rate-engine]
    CR[content-reviewer]
    CN[creator-notes]
    CC[company-context<br/>reads your profile]
    CLI[inbox command<br/>the only door to Gmail]
    G[guard hook]
  end
  Gmail[(Gmail)]
  W --> CS & NP & RE & CR & CN & CC
  CC --> P
  CN --> N
  W --> CLI --> Gmail
  CLI --> T
  G -. blocks sends and secret reads .-> W
```

- **Skills** are instructions Claude follows. They hold the method.
- **Your profile** holds the facts: your product, offer, terms, rates, voice.
  Skills never invent a fact; an empty field means "leave it out or ask".
- **The `inbox` command** is the only thing that touches Gmail. It reads mail,
  creates drafts, and runs the safety checks in code.
- **The guard hook** blocks sending and secret access around Claude.

## One run, step by step

```mermaid
sequenceDiagram
  participant You
  participant Claude
  participant inbox as inbox command
  participant Gmail
  You->>Claude: "run my inbox"
  Claude->>inbox: run start (guard armed), profile-dir, whoami, unread, drafts, score
  inbox->>Gmail: read-only calls
  Claude->>Claude: load your voice + decision compass
  loop every unread thread
    Claude->>inbox: thread <id>
    Claude->>Claude: sort into Block 0 / 1 / 2 / 3 by the highest stakes anywhere in it
  end
  Note over Claude: Block 1 (admin) first, then 2 (content), then 3 (money)<br/>heavy skills load only when their block has threads
  loop each draft
    Claude->>Claude: self-check (money? affiliate claim? "logged"? product claim?)
    Claude->>inbox: draft --thread-id ... --html-file ...
    inbox->>inbox: safety checks (recipients, attachments, links, placeholders, house style)
    inbox->>Gmail: create draft, threaded, original stays unread
  end
  Claude->>inbox: log each thread, run end
  Claude->>You: report: flagged first, then drafts by block, then skipped
  You->>Gmail: review, edit if needed, send
```

### Why blocks?

Every thread is bracketed by its **highest-stakes** signal anywhere in its history -
"sounds good" at the bottom of a thread that discussed a rate is a money thread.
Then blocks are worked lightest first:

| Block | What | Loads |
|---|---|---|
| 0 | legal structure, disputes, PR, suspicious emails | nothing - flagged for you, a safe holding draft at most |
| 1 | admin, dates, thanks, forms, program questions | your voice + the matching reply shape + the one fact needed |
| 2 | scripts, videos, drafts to review | + content-reviewer + the feedback shape + your pack's review rubric (the go-live shape only to approve) |
| 3 | rates, counters, renewals, giveaways, rights | + negotiation-playbook core + the rate card guide + your pack; each module and playbook reference only when the thread triggers it |

Two reasons. Heavy strategy only loads where the stakes justify it. And a model
holding a negotiation playbook writes a stiffer "thanks, got it" - keeping doctrine
out of context while the light replies are written keeps them sounding human.

One creator with threads in two blocks is handled entirely in the higher block, so
a money decision can never contradict an admin reply you drafted a minute earlier.

### The autonomy ladder: draft, don't ask

A question in chat costs you a context switch and produces nothing. A draft you
edit costs ten seconds and produces a sent email. So when something is unclear:

1. Resolve it from the thread, the creator's note, the profile.
2. If the missing fact is the creator's (a date, their stats), **the draft asks them**.
3. Genuinely stuck: a safe draft that moves things forward without committing money
   or terms, flagged ⚠️.
4. Only true escalations (new contract structure, disputes, legal/PR, suspicious
   emails) get no committing draft.

## Your program shapes every money email

`program.md` holds your answers - what you sell (ecommerce, saas, b2b), how you run
it (always-on, campaigns, seasonal), how money is allocated (per creator, a monthly or
campaign pot, no cash), what success means (sales, signups, reach, content,
pipeline), how fees are set (views, rate card, their quote, commission, gifting),
what a deal looks like (test then scale, one-off, ambassador) and who you work with -
plus your own two-sentence pitch. Most answers can be a list.

`inbox program` turns them into a load plan using `program/manifest.json`: the
**pack** (your business type), the **modules** (program mechanics such as affiliate,
views pricing or usage rights, each with the answer that switched it on) and the
files each block loads, with line counts. An optional `modules: +x, -y` line
overrides. The `saas` and `ecommerce` packs are built; `b2b` runs the shared core plus
your modules.

Every money thread loads the pack next to the playbook's core, and each module when the
thread triggers it (its `when` in the manifest: the affiliate module for a renewal of a
creator on commission, views pricing when a fee is priced from views; a commission
program loads the affiliate module every time). Rules that must hold even when a module
isn't loaded live in the core. So the framing follows your program: a campaign program with a fixed pot never says "we
don't work with set budgets" or "we want to work together for years"; a UGC program
prices per asset and never talks about views; a commission program opens with the
affiliate offer. Anything left blank keeps drafts neutral rather than borrowing someone
else's model.

## The money path

```mermaid
flowchart LR
  A[Money signal] --> B[Creator note: status, history]
  B -->|do-not-re-onboard / dormant| X[Graceful exit or affiliate-only]
  B -->|new / test / continue / cut| C[inbox rate: OPEN, TARGET, private MAX, verdict]
  C -->|AFFILIATE-ONLY or DECLINE-BY-MATH| X
  C -->|ask within band| D[Draft one offer: hold at OPEN or flex to TARGET]
  C -->|ask above band| E[Re-scope counter: stage-framed, affiliate after]
  C -->|no rates yet| F[Ask for their stats, flag 'set up rates']
```

The playbook's core rules: every number travels with its mechanism; creators move
the price, you move the deliverable; a first deal is two pieces, so each gets a fair
read; the affiliate never sits in our first number; MAX and break-even never reach a
creator.

## How it learns

After each run, `inbox score` compares every draft with what you actually sent on
that thread. Unedited sends count toward the zero-edit rate (target 90%+). Edits
become candidate rules: wording goes into your `voice.md`, decisions into
`house-rules.md`, facts into the right profile file. Nothing changes without your OK,
and the plugin's own files are never edited on your machine - improvements that
would help everyone come back through GitHub issues.

## Where to look in the repo

```
plugins/creator-management-inbox/
  program/                       manifest.json + business packs and program modules
  skills/
    inbox-auto-draft-workflow/   the orchestrator + compass + reply shapes
    comms-style/                 voice engine + a fictional example voice
    voice-builder/               builds your voice.md
    negotiation-playbook/        rates and terms strategy (+ deep references)
    rate-engine/                 the numbers (simple + advanced warehouse mode)
    content-reviewer/            script and video review
    creator-notes/               one note per creator
    company-context/             reads your profile; templates live here
    inbox-setup/                 guided setup + the Gmail guide
  scripts/inbox.py               the inbox command
  hooks/guard.py                 the send guard
  demo/                          fictional inboxes + profiles: Fernwell (saas, the default)
                                 and Quillmoss (`demo_profile: ecommerce` in settings.md)
```
