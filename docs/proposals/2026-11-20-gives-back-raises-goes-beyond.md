# Proposal: say whether each upgrade gives back, raises, or goes beyond

Written 2026-11-20, at John's request, after a conversation about the philosophical critiques of
transhumanism (Nicholas Agar, Susan Schneider, Nick Bostrom and others) and what they offer this
project.

**This is a proposal. Nothing live has changed.** It was written against the record on `main` at
commit 842bdca (2026-11-15): 35 upgrades, 28 of them at "first human" or above. The first pass in
section 5 was made by reading every upgrade's test ("what would count") as it stands there.

## 1. The recommendation, in short

Add one field to every upgrade saying what the change does for the person who has it:

- **gives back** something lost or missing (a deaf person hears),
- **raises** a healthy person within the range unaided people already reach (a healthy adult learns
  faster),
- **goes beyond** anything an unaided person can do (a person senses a magnetic field).

Keep the headline exactly as ruled on 2026-10-16. Add one line under the five stage totals that
splits the headline count three ways. On the first pass that line would read roughly:

> Of the 28 tried in a person: 20 give back something lost, 6 raise a healthy person, 1 goes
> beyond what any unaided person can do, and 1 is not classed.

Those four numbers are provisional. They depend on the rulings in section 10 and on seven hard
cases in section 6, and the session that builds this checks each one against its stage record.

## 2. The gap

The stage ladder says how far a technology has travelled. It does not say what the technology does
for the person. A cochlear implant and a device that gives a person a new sense each count as one
upgrade at their stage. A visitor who reads "28 of 35 ways of changing a human being with
technology have been tried in at least one living person" cannot tell whether that means 28 kinds
of medicine or 28 kinds of superhuman. On the first pass it is mostly medicine, and the site
cannot currently say so.

The distinction comes from Nicholas Agar, who separates moderate enhancement (within the range
humans already reach) from radical enhancement (far past it) in *Truly Human Enhancement* (MIT
Press, 2014; details written from memory, to be verified before the book is cited anywhere
public). Agar uses the line to argue for limits. This proposal takes only the line, as a fact
about each test, and takes no side on his argument. The charter's rule stands: the tracker does
not judge whether changing ourselves is desirable.

## 3. The field

| Field | Required | Meaning |
|---|---|---|
| `gain` | yes, on every upgrade | One of `gives-back`, `raises`, `goes-beyond`, `not-classed`. |
| `gain_note` | for `not-classed`, and for any hard case | One or two plain sentences: why this class, and what the nearest other reading was. |

New export rule: every upgrade has a `gain` with one of the four values, and a `not-classed` entry
has a `gain_note`. A later change to `gain` gets a `revisions` entry like any other field.

The public words would be "gives back", "raises" and "goes beyond". The word "gain" stays in
`docs/` and `scripts/`, under the rule that public pages use no internal vocabulary.

## 4. The rule for choosing a class

Three parts. Each is a judgment call and each has a real alternative (section 11).

1. **Read the test as written.** The class comes from who the test names and what it says they
   can do afterwards. "A person with paralysis controls a cursor" gives back. If the same implant
   is one day put in a healthy person, that is a different test and so a different upgrade, added
   at the yearly review. The class of the existing entry does not move.
2. **Compare with a healthy adult.** Bringing a person up to what a typical healthy adult can do
   is giving back, whether the cause was injury, illness or a condition from birth. Preventing a
   named disease counts as giving back too. Lifting a healthy person higher, but not past the best
   unaided people, is raising. Past the best unaided person, or a kind of ability no unaided
   person has at all, is going beyond.
3. **Judge by what the person can do, not by how the signal travels.** A headset that lets a
   healthy wearer move a cursor by brain signals uses a new route, but the wearer can do nothing a
   hand could not. Under this rule that is not going beyond.

`not-classed` is for an upgrade whose test is not about what a person can do: a test in an animal
with no human version written yet, or a test that counts how many people use a tool.

## 5. First pass on all 35

Stage in brackets. A star marks a hard case discussed in section 6.

**Senses**
- An implant gives a blind person back some sight [in clinical use]: gives back
- A cochlear implant gives a deaf person hearing [in wide use]: gives back
- A gene therapy restores sight in an inherited blindness [in clinical use]: gives back
- A gene therapy restores hearing in a child born deaf [in clinical use]: gives back
- An implant in the visual cortex gives sight with no working eyes [first human]: gives back
- A device gives a person a sense no human is born with [first human]: goes beyond

**Movement and body**
- A prosthetic arm moves by thought and feeds back touch [first human]: gives back
- A powered exoskeleton lets a paralysed person walk [in clinical use]: gives back
- A spinal implant lets a paralysed person walk again on their own legs [first human]: gives back
- A prosthetic limb fixed to the bone with nerve control [first human]: gives back
- A gene therapy builds stronger muscle in a healthy body [shown in animals]: raises

**Memory and thinking**
- A brain implant improves memory recall in a person [first human]: raises *
- A drug raises a measured thinking ability in healthy adults [idea only]: raises
- An always-on AI assistant is used daily by most adults in a country [in wide use]: not classed *
- Electrical stimulation improves learning in healthy adults [first human]: raises

**Mood and drive**
- A brain implant lifts severe depression [first human]: gives back
- A closed-loop implant detects a mood state and corrects it automatically [first human]: gives back
- A psychedelic therapy is approved for prescription [in clinical use]: gives back
- A treatment removes a specific fear memory [first human]: raises *

**Lifespan and repair**
- A drug makes people live longer in good health [shown in animals]: raises *
- Partially resetting cells reverses ageing in a living animal [shown in animals]: gives back *
- A drug clears aged cells from a person's body [first human]: gives back *
- An organ from a gene-edited pig keeps a person alive [first human]: gives back
- A printed or lab-grown organ works in a person for a year [first human]: gives back

**Inheritance**
- A child is born from a gene-edited embryo [first human]: raises *
- A baby is born with donor mitochondria to avoid an inherited disease [in clinical use]: gives back
- Embryos are chosen by a genetic score for traits, not disease [in clinical use]: raises
- A mammal is carried to birth in an artificial womb [idea only]: not classed *

**The link to machines**
- A fully implanted wireless brain chip lets a paralysed person control a computer [first human]: gives back
- A wired brain implant lets a paralysed person control a cursor [first human]: gives back
- A brain implant turns intended speech into text at conversational speed [first human]: gives back
- A brain implant gives a person touch from a robotic hand [first human]: gives back
- A headset worn on the scalp controls a device without surgery [in wide use]: raises *
- An uploaded animal brain reproduces something it learned [idea only]: not classed *
- A brain link carries more information per second than speech [idea only]: goes beyond

**Totals on this pass**

| | All 35 | The 28 at first human or above | The 10 in clinical or wide use |
|---|---|---|---|
| Gives back | 21 | 20 | 7 |
| Raises | 9 | 6 | 2 |
| Goes beyond | 2 | 1 | 0 |
| Not classed | 3 | 1 | 1 |

The plain reading: today nothing that goes beyond the human range is available from a doctor or
on general sale, and exactly one such thing (a new sense) has been tried in a person.

## 6. The hard cases

Each needs a ruling, or a note saying why it sits where it does.

1. **The memory implant.** The test names no condition, only "a person with electrodes implanted
   in the brain". The class depends on who the recorded people were. If they were patients who
   already had electrodes for another reason and scored above their own usual level, "raises" fits.
   If the record is about repairing a damaged memory, "gives back" fits. The building session
   reads the stage record and says which.
2. **Removing a specific fear memory.** A phobia treated this way is giving back. A learned fear
   removed in a healthy volunteer is something else, and no unaided person can delete a chosen
   memory, which argues for "goes beyond". First pass says "raises" as the middle reading. This is
   the least certain call on the list.
3. **Ageing (three entries).** Is growing old a loss to be given back, or the healthy baseline?
   The rule in section 4 compares with a healthy adult, so clearing aged cells and resetting cells
   towards youth are "gives back", and a drug that adds healthy years without passing the longest
   recorded human life is "raises". The alternative treats ageing as normal, which would make all
   three "raises" and move one of the 28 from "gives back" to "raises". Outrunning Ageing has the
   same question underneath it, so the two sites should rule it once.
4. **The gene-edited child.** The test is neutral about what the edit is for. The births on record
   aimed at resistance to an infection, a trait some people are born with, so "raises". An edit to
   remove a named inherited disease would be "gives back", and under rule 1 that would be a
   separate upgrade.
5. **The scalp headset.** By the route it is new, by what the wearer can do it adds nothing a hand
   cannot. Rule 3 puts it at "raises", and even that is generous. The alternative is "not
   classed". If rule 3 is rejected it becomes "goes beyond", and the site would then say a
   beyond-human upgrade is in wide use, which a visitor would be right to find misleading.
6. **The always-on AI assistant.** Its test counts how many adults use a tool that sits outside
   the body, so "not classed". The alternative is to class the person plus the tool, which opens
   the door to classing a library card.
7. **The artificial womb and the uploaded animal brain.** Neither test is about what a living
   person can do. "Not classed", with the note saying so.

## 7. What the site would show

- **Home page:** the headline and the five stage totals unchanged. One new line under them with
  the three-way split of the headline count.
- **Each branch page and each upgrade page:** the class in plain words beside the stage.
- **The method page:** the rule from section 4 and the hard cases with their notes.
- **`data/headline.json`:** the split added, computed by the export and never typed in.

Not proposed: shading the figure by class, or a second headline. The figure already carries one
meaning (furthest stage reached) and should keep it.

## 8. The claims log: two leads, no new entries

The log already enters critics on the same terms as advocates: Miguel Nicolelis (two entries),
Susan Schneider (three) and Andrew Jackson among them, and Bostrom's 2014 argument that a faster
brain link is the wrong bottleneck. So the log does not need a round of critics. Two leads are
worth adding to `data/claims/not-entered.toml` as "to add", both written from memory and
unchecked:

- Nick Bostrom, "The Future of Human Evolution" (2004, in the collection *Death and Anti-Death*
  edited by Charles Tandy): an argument that competition among enhanced or uploaded minds could
  select away what people value. It bears on the merger idea directly, from someone the log
  already carries as an advocate of enhancement.
- Nicholas Agar, *Humanity's End: Why We Should Reject Radical Enhancement* (MIT Press, 2010): a
  book-length reply to Kurzweil and others the log already carries.

Each becomes an entry only when its text has been read and a short phrase checked, under the
existing rules. Sandel, Habermas and Bernard Williams argue about whether enhancement is
desirable, which the charter puts out of scope, so they are not proposed.

## 9. Considered and not proposed

- **A "can it be undone" field.** A good question for every upgrade, but for most early-stage
  entries the honest answer is "not known", so the column would be mostly empty. Hold until the
  parked essay "The Exit Cost" has defined the test, then raise it at the yearly review.
- **A strongest-objection note on each branch.** This would be the site's first statement about
  what ought to be done. The charter rules that out. The material belongs in a Sentient Horizons
  essay that links to the tree.

## 10. Rulings asked for

1. Add the `gain` field to every upgrade: yes or no.
2. The rule in section 4, all three parts, as written or changed.
3. Ageing: a loss to be given back (as proposed), or the healthy baseline.
4. The seven hard cases in section 6, each as proposed or moved.
5. The display in section 7: one line under the stage totals, headline unchanged.
6. The two claims-log leads in section 8: add or leave.

## 11. Each design choice, with confidence and the strongest alternative

| Choice | Confidence | Standard or judgment | Strongest alternative and its cost |
|---|---|---|---|
| Three classes plus "not classed" | Moderate to high | Follows the therapy and enhancement distinction long used in bioethics, with Agar's split of enhancement into two | Two classes (treatment, enhancement): simpler, but hides the one number visitors most want, how much goes past the human range |
| Class read from the test as written | High | Judgment (Claude) | Class by the furthest use on record: tracks the world more closely, but the field would drift and one entry would mean two things |
| Healthy adult as the comparison | Moderate | Judgment; standard in medicine, disputed for ageing and for conditions from birth | The person's own earlier state: fails for anyone born with a condition |
| Judged by what the person can do, not the route | Moderate | Judgment | By route: simpler to apply, but calls a toy headset beyond-human |
| Headline unchanged, split shown beneath | High | Follows the 2026-10-16 ruling on the headline | Lead with the "goes beyond" count: more striking, and it would rest the front page on the least settled calls |
| Words "gives back, raises, goes beyond" | Moderate | Judgment on wording | "Restores, improves, exceeds": more formal and closer to the literature |

One thing I would watch on reflection: the count of "raises" among the 28 rests on four starred
entries out of six. If the hard cases are ruled differently, that number moves more than the
others, and the method page should say so.

## 12. What building it takes

One session after the rulings: add the field and rule to `docs/upgrade-schema.md` and
`scripts/export.py`, tag the 35 upgrades with a note on each hard case, extend the headline file
and its test, add the line and labels to the site, write the method-page section, and add a dated
line to `CHANGELOG.md`. No stage, date or count already published changes.
