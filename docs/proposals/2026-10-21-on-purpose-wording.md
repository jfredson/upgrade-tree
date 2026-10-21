# Proposal: a better way to say "on purpose"

Written 2026-10-21, at John's request: "Can we review the use of the words 'on purpose' in the copy
for the Upgrade Tree project? Something about that just feels off. There has to be a better way to
say what we are trying to convey for that project."

**This is a proposal. Nothing live has changed.** It lists every public use of the phrase, says why
it reads off, sets out four other ways to say it with the headline, home page, definition and
today's share pair written out for each, and recommends one. John picks; a later session makes the
change.

## 1. The recommendation, in short

Say how the change is made, once, where the phrase now stands on its own: **"How much of a human
being can we change with technology today?"** and **"28 of 35 ways of changing a human being with
technology have been tried in at least one living person."** In the many sentences that already
spell out "a device, a drug or a surgery", drop "on purpose" and add nothing, because the sentence
already says it. This changes how the site sounds, not what it counts. The full reasoning is in
section 5.

## 2. Why "on purpose" reads off

**It makes the reader picture the opposite.** "On purpose" is what we say to rule out "by
accident". Put it in the headline and a reader half pictures accidental changes to a person, which
nobody was thinking about, and the sentence sounds as if it is answering a charge. It is also a
playground phrase ("you did that on purpose"), so it carries a faint note of blame, which is
strongest exactly where the site least wants it: next to the gene-edited children.

**It hides the real dividing line instead of saying it.** The phrase is there to separate the
changes the tree counts from the ones it does not. But the line the site draws is not between
intended and accidental. It is between changes made with a technology and everything else that
changes a person: growing up, ageing, illness, school, exercise. Those are often on purpose too
(nobody trains for a marathon by accident), so "on purpose" does not actually draw the line. The
reader has to work it out from the sentence that follows.

**The site already says it better, one sentence later.** The home page's opening goes straight on:
"today, with a device, a drug or a procedure that at least one person has actually had". That
clause is the real definition. "On purpose" is a placeholder for it.

**Checking the master session's starting thought against the method page.** The method page's
definition is: "An upgrade is one specific technology that changes a human being on purpose: a
device, a drug, a procedure, or a practice such as leaning on an always-on AI assistant." So the
starting thought is right, with two corrections:

- **It is not only devices, drugs and surgery.** A practice counts too, if it is built on a
  machine: the tree has an upgrade for an always-on AI assistant used daily by most adults in a
  country, with no implant at all. The share posts' "a device, a drug or a surgery" leaves this
  out; that is fine for a short post, but the definition must keep it.
- **It covers repair as well as improvement.** More than half of the tree gives back something lost or treats an illness:
  sight to the blind, hearing to the deaf, walking to the paralysed, relief from severe depression.
  The rest adds or alters: a sense no human is born with, longer life, an edited embryo. So the
  wording must not lean toward "enhancement" alone.

**One branch uses the phrase to mean something else.** The mood branch says a change counts "on
purpose and for a reason the person chose", and the psychedelic therapy upgrade says "on purpose
and at their request". There the words carry a second idea, that the person chose it. That is a
real condition on that branch, and it survives the rewording below ("for a reason the person
chose" stays). It sits a little oddly beside the method rule that a first human "does not need
permission", but that rule is about whether a thing has been done at all, not about which branch it
belongs on, so this proposal leaves both alone. It is noted here only so the rewording does not
quietly drop the condition.

**Some uses are right and stay.** Several upgrade tests use "on purpose" or "deliberately" to mean
the person meant the action rather than hitting it by chance: a paralysed person "moves a cursor
... on purpose, at a rate better than chance"; a scalp headset lets the wearer "deliberately
control something". That is exact, and it is test wording, so it does not change. Ordinary uses
such as "the test above is stricter on purpose" also stay.

## 3. Every use, grouped by its job

Counted on 2026-10-21 from `main` of upgrade-tree (commit 21ea60b) and `master` of
sentient-horizons (commit 5544148). Files the export writes (`site/src/data/tree.json`,
`data/headline.json`, `site/src/data/readings.json`, sentient-horizons'
`site/src/data/projects-live.json`) are not listed separately: they follow their sources.

### The headline count

| Where | The words now |
|---|---|
| upgrade-tree `scripts/export.py:1085` (writes `data/headline.json`) | "28 of 35 ways of changing a human being on purpose have been tried in at least one living person" |
| `site/src/pages/index.astro:37` (home page, under the big number) | same sentence |
| `site/src/pages/claims.astro:138` (the claims page) | same, plus "counted from the public record" |
| `site/src/content/news/2026-10-18-start-here.md:2` (the pinned post's title) | "Start here: of 35 ways to change a human being on purpose, 28 have been tried in a person" |
| sentient-horizons `site/src/data/projects.toml:125` (the family page's label) | "ways of changing a human being on purpose have been tried in at least one living person" |
| sentient-horizons share kit `ops/tracker-news/share-kits/upgrade-tree-2026-10-18-start-here.md:1, 10`, and the week's plan `ops/substack/notes/2026-10-19-week-1.md:296` | the pinned post's title, quoted |

### The question (the site's one-line description of itself)

| Where | The words now |
|---|---|
| `site/src/pages/index.astro:47` (home page heading) | "How much of a human being can we change on purpose today?" |
| `site/src/layouts/Base.astro:22` (the description search engines and link previews show) | the question, then the count's description |
| `site/src/layouts/Base.astro:82` (the share card's text for people using screen readers) | "The Upgrade Tree: How much of a human being can we change on purpose today?" |
| `site/src/layouts/Base.astro:95` (footer) | "A public count of how much of a human being we can change on purpose today, ..." |
| `scripts/social-image.mjs:80` (the share card image) | the question, over three lines |
| `README.md:3` | the question |
| `CLAUDE.md:8` | "A public tracker of how much of a human being we can change on purpose today" |
| `site/src/content/news/2026-10-18-start-here.md:15` (pinned post) | "It asks one question: how much of a human being can we change on purpose today?" |
| `data/mind.toml:94` (a note on the AI assistant upgrade) | "the charter's question is how much of a person we can change on purpose" |
| sentient-horizons `site/src/data/projects.toml:123` | the question |
| sentient-horizons `design/README.md:80`, `design/tracker-pattern.md:64` (design notes, not public) | the question |
| sentient-horizons `ops/tracker-news/opening-posts/upgrade-tree.md:10, 18` (the opening post's first draft) | the question and the count |
| sentient-horizons share kit and week's plan: X options B and C, Note options 1 and 2 (kit lines 29, 35, 43, 49; plan lines 96, 102, 110, 116) | "how much of a human being we can really change on purpose today", "the ways a person can be changed on purpose" |
| sentient-horizons `ops/substack/drafts/2026-10-18-outrunning-ageing-substack.md:151` (a draft) | the question and the count, quoted |

### What an upgrade is

| Where | The words now |
|---|---|
| `site/src/pages/index.astro:83` (home page, "An upgrade, here, is...") | "one specific way of changing a human being on purpose" |
| `site/src/pages/method.astro:21` | "one specific technology that changes a human being on purpose" |
| `docs/upgrade-schema.md:16` (the rules for the record, not public) | same as the method page |
| `README.md:5` | "the specific ways a person can be changed on purpose" |
| `site/README.md:55` | "...changing a human being on purpose; it recommends nothing" |
| `site/src/layouts/Base.astro:108` (footer notice) | "what has been promised about changing a human being on purpose" |
| `site/src/pages/branches/index.astro:7` (the branches page description) | "The seven things about a person that can be changed on purpose" |
| `.github/ISSUE_TEMPLATE/missing-upgrade.md:3` (the form for suggesting an upgrade) | "A way of changing a person on purpose that the tree does not list" |
| sentient-horizons `site/src/data/projects.toml:124` | "the specific ways a person can be changed on purpose" |

### Individual upgrades and the mood branch

| Where | The words now | Proposed, under any direction |
|---|---|---|
| `data/mood.toml:109` (name) | "A treatment removes a specific fear memory on purpose" | "A treatment removes a specific fear memory". "Specific" already carries it, and the test says the fear is "identified in advance". |
| `data/inheritance.toml:8` (name) | "A child is born from an embryo whose genes were edited on purpose" | "A child is born from a gene-edited embryo". "Edited" already means someone meant it; the test says the rest. |
| `data/mood.toml:83` (psychedelic therapy description) | "how a person feels, on purpose and at their request" | "how a person feels, at their request" |
| `data/branches.toml:44` (mood branch tagline) | "How we feel, what we want, and whether that can be set on purpose." | "How we feel, what we want, and whether we can choose to change it." |
| `data/branches.toml:47` (mood branch meaning) | "by a drug, a device or a procedure, on purpose and for a reason the person chose" | "by a drug, a device or a procedure, for a reason the person chose" |

The two upgrade ids (`mood-treatment-removes-a-specific-fear-memory`,
`inheritance-child-born-from-a-gene-edited-embryo`) never had the phrase, so no web address
changes. Names are not ids and can change; each rename gets a changelog line.

### Everything else: kept as it is

- **Test wording, where "on purpose" or "deliberately" means the person meant the action:**
  `data/link.toml:52` (the wired implant's cursor), `data/link.toml:148` (the scalp headset),
  `data/mood.toml:119` and `data/inheritance.toml:19` (the fear-memory and embryo tests, where the
  words say the change was targeted). Changing a test is a change to the record, not to the voice.
- **Ordinary uses:** `data/link.toml:265` ("deliberate output", a measured rate), `data/mind.toml:50`,
  `data/movement.toml:36`, `data/inheritance.toml:134` ("stricter on purpose" and the like), the
  long-shot label on an upgrade page (`site/src/pages/branches/[branch]/[id].astro:36`, "Long shot,
  kept on the tree on purpose"), and the scalp headset news post's "deliberately controlling a
  device".
- **History:** `CHANGELOG.md` and its copy in `site/src/data/changelog.json`, sentient-horizons'
  `design/review-2026-10-16/README.md` and `editorial/essay-workbench/outrunning-ageing-cut-material-2026-10-18.md`.
  They record what was said on their dates.
- **Essays and about pages in sentient-horizons:** none use the phrase about the tree. The Outrunning
  Ageing essay names The Upgrade Tree without it.

## 4. Four directions

Each direction gives the headline sentence, the home page's question and opening, the
one-sentence definition, and Wednesday 2026-10-21's pair (the "Start here" share kit's recommended
X post, option B, and Note, option 1), kept as close to the drafts as the change allows. X counts
are with the link counted as 23 characters; all are under 280. In every direction the home
page's opening sentence after the question stays as it is ("Not in a story, and not someday:
today, with a device, a drug or a procedure that at least one person has actually had, counted
from the public record and never guessed."), because it already says how.

### Direction A: say how, "with technology" (recommended)

- **Headline:** 28 of 35 ways of changing a human being with technology have been tried in at
  least one living person.
- **Question:** How much of a human being can we change with technology today?
- **Definition (home page):** An *upgrade*, here, is one specific way technology can change how a
  person's body or mind works: an implant that gives back some sight, a pill meant to slow ageing,
  a chip that lets a paralysed person type by thought.
- **Definition (method page):** An upgrade is one specific technology that changes how a human
  body or mind works: a device, a drug, a procedure, or a practice such as leaning on an always-on
  AI assistant. It counts whether it gives back something lost or adds something new. (The last
  sentence is new; it says what the tree already does.)
- **X post** (277 characters): I've wanted to know how much technology can really change a human
  being today: not in a story, but with a device, a drug or a surgery someone has actually had. So
  I started a public count from the record. Today it stands at 28 of the 35 ways it follows.
  https://theupgradetree.com/news/2026-10-18-start-here/
- **Substack Note** (106 words): One idea about the future says that as machines get smarter,
  people will keep up by joining with them: sharper senses, better memory, a longer life, and in
  the end a direct line from the brain to a computer. Some of that is already happening, and some
  of it is only talk. I wanted to know which was which, so I started a public count of the ways
  technology can change a human being, with a device, a drug or a surgery that at least one person
  has actually had. Today 28 of the 35 it follows have been tried in someone. Here's where it
  stands: https://theupgradetree.com/news/2026-10-18-start-here/
- **Does it change what counts?** No. The method page already calls every upgrade "one specific
  technology", the AI assistant practice included. It only says out loud the line the phrase was
  hinting at. One thing to watch: some readers do not think of a drug as technology. The
  definition names drugs in the next breath, which settles it.

### Direction B: name the thing, "upgrade"

- **Headline:** 28 of 35 upgrades have been tried in at least one living person.
- **Question:** How much of a human being can we upgrade today?
- **Definition (home page):** An *upgrade*, here, is one specific change to how a person's body
  or mind works, made with a device, a drug or a procedure: an implant that gives back some sight,
  a pill meant to slow ageing, a chip that lets a paralysed person type by thought.
- **X post** (257 characters): I've wanted to know how much of a human being we can really
  upgrade today, with a device, a drug or a surgery someone has actually had. So I started a public
  count from the record. Today it stands at 28 of the 35 upgrades it follows.
  https://theupgradetree.com/news/2026-10-18-start-here/
- **Substack Note** (104 words): as option 1, with the middle sentence: "I wanted to know which was
  which, so I started a public count of the upgrades a person can have today: a device, a drug or
  a surgery that at least one person has actually had."
- **Does it change what counts?** No, but it changes the sound more than it looks. The headline
  becomes the shortest of the four and matches the site's name. But "upgrade" means "better", and
  the site takes no side: its footer says it "recommends nothing". Calling an edited embryo or the
  removal of a memory an upgrade, in the headline itself, sounds like approval. On a share card a
  stranger also meets "upgrades" before anything defines it. The word works as the name of each
  entry, defined right under the count, which is how the site uses it now.

### Direction C: recast the question, "redesign"

- **Headline:** 28 of 35 ways of redesigning a human being have been tried in at least one living
  person.
- **Question:** How much of a human being can we redesign today?
- **Definition (home page):** An *upgrade*, here, is one specific change to how a person is built
  or how they work, made by design: an implant that gives back some sight, a pill meant to slow
  ageing, a chip that lets a paralysed person type by thought.
- **X post** (254 characters): I've wanted to know how much of a human being we can really
  redesign today, with a device, a drug or a surgery someone has actually had. So I started a public
  count from the record. Today it stands at 28 of the 35 ways it follows.
  https://theupgradetree.com/news/2026-10-18-start-here/
- **Substack Note** (106 words): as option 1, with "a public count of the ways a human being can be
  redesigned, with a device, a drug or a surgery that at least one person has actually had."
- **Does it change what counts?** Not the rules, but it changes what a reader expects to find,
  which is nearly the same thing. It is the boldest and most memorable, and it fits the idea of
  merging with machines. But "redesign" means building a different kind of person, and more than half of
  the tree is repair: nobody would say a cochlear implant redesigns a deaf child, and some people
  who are deaf or disabled would take that framing badly. Next to the inheritance branch it also
  calls up "designer babies", which takes a side. It would pull the site toward enhancement and
  make the repair upgrades look out of place.

### Direction D: drop the phrase and let the means do the work

- **Headline:** 28 of 35 ways of changing a human being have been tried in at least one living
  person.
- **Question:** How much of a human being can we change today?
- **Definition (home page):** An *upgrade*, here, is one specific way of changing how a person's
  body or mind works with a device, a drug or a procedure: an implant that gives back some sight,
  a pill meant to slow ageing, a chip that lets a paralysed person type by thought.
- **X post** (252 characters): I've wanted to know how much of a human being we can really change
  today, with a device, a drug or a surgery someone has actually had. So I started a public count
  from the record. Today it stands at 28 of the 35 ways it follows.
  https://theupgradetree.com/news/2026-10-18-start-here/
- **Substack Note** (106 words): as option 1, with "a public count of the ways a human being can be
  changed with a device, a drug or a surgery that at least one person has actually had."
- **Does it change what counts?** No. It is the lightest touch, and in sentences that spell out
  "a device, a drug or a surgery" it is the best reading of all: the X post above is today's
  recommended draft with two words gone. But where the question or the headline stands alone (the
  share card, the link preview, the footer, the headline file other sites read), "change a human
  being" is too wide: school, love, prison and ageing all change a human being. Those places need
  something to say how.

### Considered and set aside

- **"Deliberately."** More grown-up than "on purpose" but the same idea, so the same problem: it
  still rules out an accident nobody raised.
- **"With medicine and machines."** Concrete and warm, and close to Direction A. But "medicine"
  suggests treating illness, and much of the tree is not treatment.
- **"By design."** Direction C's problem in a softer form.

## 5. Recommendation

Take Direction A where the phrase stands alone, and Direction D everywhere else. "With technology"
is the plain name for the line the site actually draws (the method page already calls every upgrade
"one specific technology"), it covers the AI assistant practice and the repairs as well as the
enhancements, it takes no side, and it points at the idea the whole project is built around,
people joining with their machines. Where a sentence already says "a device, a drug or a surgery",
adding "with technology" would say it twice, so there the phrase simply goes. "Upgrade" stays the
name of each entry, defined just under the count, which is where it works.

## 6. What would change if John picks the recommendation

- **The Upgrade Tree: 26 lines in 17 files.** The headline (one line in the export script, then
  re-run the export), the home page (3), the claims page, the method page, the branches page, the
  layout (4: description, share card text, footer line, footer notice), the share card image
  script (then rebuild the image), the two READMEs (3), `CLAUDE.md`, the rules for the record, the
  suggestion form, the mood branch (2), the two upgrade names, the psychedelic description, the
  note on the AI assistant upgrade, and the pinned post (title and one sentence; its address stays
  `/news/2026-10-18-start-here/`). Plus one changelog entry saying what changed and why.
- **Sentient Horizons: 3 lines on the family page** (`site/src/data/projects.toml`, the question,
  description and label), then its export; 2 design notes; and the drafts not yet posted: the
  "Start here" share kit and the week's plan (title quoted 3 times, 4 post options in each), and
  the Outrunning Ageing Substack draft if it has not gone out. About 20 lines, most of them in
  drafts.
- **Left as they are:** the tests, the ordinary uses, the changelog's past entries, and anything
  already posted.
- **If John posts today's pair before this lands,** it goes out with the old wording. That is fine:
  posted words are a record, and the next pair uses the new ones.

Nothing here touches a count, a stage, an id or a test. `python3 scripts/export.py --check` will
need the export re-run after the headline line changes, because the headline file must match the
words the export writes.
