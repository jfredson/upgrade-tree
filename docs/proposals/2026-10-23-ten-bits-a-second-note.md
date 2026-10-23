# Proposal: a note on the link branch about the ten-bits-a-second finding

Written 2026-10-23, at John's request of 2026-10-22: "draft a note for the Upgrade Tree's link
branch about the 10 bits a second finding, for me to review." It grew out of the Sentient Horizons
essay draft on Sam Altman's AI device, where a check of the merger argument against current brain
science turned up the finding.

**This is a proposal. Nothing live has changed.** John picks; a later session makes the change.

## 1. The finding, and why it bears on the tree

The link branch's second number is how much information can pass between a brain and a machine
each second. The page says why it matters: "The merger argument has rested on one number since
2017: how much information can pass between a brain and a computer each second, and whether that
can beat the mouth and the hands."

Jieyu Zheng and Markus Meister, of the California Institute of Technology, argue that the mouth and
the hands are not what holds people back ("The unbearable slowness of being: Why do we live at
10 bits/s?", *Neuron*, published online 2024-12-17, https://doi.org/10.1016/j.neuron.2024.11.008;
read in full on 2026-10-23 in the authors' open copy, arXiv 2408.10234 version 2). What the paper
says, checked at the source:

- Human behaviour carries information at about 10 bits a second, while the senses gather it at
  about a billion bits a second, and "This enormous ratio – about 100,000,000 – remains largely
  unexplained" (section 2, the introduction).
- The same figure holds across the activities they examine: a fast typist (the 120 words a minute
  the tree already uses as its "fast typist" reference line), speech at 13 bits a second, and
  memory contests, "within a factor of two of our ballpark number of 10 bits/s" (section 3).
- On typing, they answer the objection that the fingers are the bottleneck by turning to speech,
  a motor system "that evolved for communication", and find it only slightly faster (section 3).
- Section 6.3, "The Musk illusion", quotes Musk on Neuralink's purpose ("we have a bandwidth
  problem. You just can't communicate through your fingers. It's just too slow") and answers:
  "we predict that Musk's brain will communicate with the computer at about 10 bits/s." They add
  that a telephone, whose data rate was designed to match language, would do as well.
- Section 6.4, on brain-computer interfaces for patients, says such devices "could greatly
  benefit" people who cannot speak, and that "one really needs to convey only a few bits per
  second to and from the brain".

The tree's own figures fit their view so far. The best pointing figure is Neuralink's 8 bits a
second (the company's own measurement), against about 10 for its engineers with a mouse. The best
text figure is 78 words a minute, against 120 for a fast typist and 160 for conversation.

This is one paper's argument, not a settled result. They say plainly that the cause of the limit
is unexplained. I have not searched for published replies to it; that search is the second step in section 4.

## 2. Recommendation: one paragraph on the link branch's page

Add one paragraph to the introduction of "The second number" on the link branch page
(`site/src/pages/branches/[branch]/index.astro`, the `bw-intro` block), after the two paragraphs
that give the best figures. It is page text, not a record, so it changes no figure, stage or count.

The paragraph, as it would read:

> **A caution about what this number can show.** A faster link helps only if the link is what
> holds a person back. In [a paper in the journal *Neuron*](https://doi.org/10.1016/j.neuron.2024.11.008)
> published in December 2024 ([open copy](https://arxiv.org/abs/2408.10234)), the neuroscientists
> Jieyu Zheng and Markus Meister estimate that everything people do, from typing and speaking to
> memorising in memory contests, carries information at about 10 bits a second, while our senses
> take in about a billion. (A bit is the smallest piece of information, a single yes or no.) On
> their reading the limit lies in thinking itself, not in the fingers or the mouth, and nobody yet
> knows why it is so low. They take on the merger argument by name, calling the hope for a much
> faster link "the Musk illusion" after [Elon Musk](https://en.wikipedia.org/wiki/Elon_Musk), and
> predict that his brain, linked to a computer, would communicate at about 10 bits a second. So far
> the figures here fit their view: the best pointing figure is about what an engineer manages with
> a mouse, and the best text figure is below a fast typist. If they are right, these lines will
> level off near the rates a reader already has, and the value of a brain link will lie in what it
> gives back to people who cannot type or speak. A brain link that carried text or pointing well
> above those rates would be evidence against them, and it would show up here first.

Why this form. Moderate to high confidence; a judgement call, not standard practice. The page
already explains why the number matters, so a caution about what it can show belongs beside that
explanation, where the reader meets the number. It names a test that could prove the caution
wrong, which keeps it a statement about evidence rather than a verdict on the merger idea. And it
is page text, so the record's rule that talk and delivery are never mixed is untouched.

## 3. Alternatives

1. **A reference line at 10 bits a second on the pointing chart**, labelled "All human behaviour,
   as information". Cost: it would sit on top of the existing "Engineers with a mouse" line at
   about 10, and it would put a general estimate across all behaviour on a chart of one task.
   It adds little the paragraph does not say better.
2. **A news post.** The site's rules let a post only explain a change the records already carry,
   and this changes no record, so a post would need the claims-log entry in section 4 first.
3. **Nothing on the page; the paper enters the claims log only** (section 4). Cost: a reader of the
   chart never meets the caution, which is the one place it matters.

## 4. Two further steps, each for John to decide

1. **Enter the paper in the claims log as a critic.** Section 6.3 is a dated, sourced statement
   about humans merging with machines, from named scientists, which is what the log records; the
   log already enters critics on the same terms (Susan Schneider, 2019). It would be the log's
   first entry from people who measured the thing the argument rests on. Suggested id:
   `2024-12-17-zheng-meister-the-musk-illusion`, `critic = true`, quoting "we predict that Musk's
   brain will communicate with the computer at about 10 bits/s". Once entered, it could carry a
   short news post of the kind "a claim added".
2. **Search for replies before publishing.** A fair caution should say whether the estimate has
   been challenged in print. Not done yet: run a search for responses to the paper (letters in
   *Neuron*, preprints, commentary by brain-computer interface researchers) and add one sentence if
   a serious objection exists.

## 5. Related change elsewhere

The essay draft that prompted this ("Sam Altman says AI needs a new kind of device", Sentient
Horizons, branch `claude/two-roads-draft-2026-10-22`) cites the same paper. Its paragraph says the
finding "does not make the keep-up argument wrong". Having read the full paper, that is softer than
the paper itself, which calls the argument an illusion. The draft should say so, and then say why
the essay still holds its view.
