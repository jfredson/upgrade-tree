# Reading notes: Neuralink's Telepathy and Blindsight, against Musk's posts of 2026-10-30

Written 2026-10-31 by a session the planning session for the tracker sites started, for the news post
`site/src/content/news/2026-10-31-musks-claims-for-telepathy-and-blindsight-beside-the-record.md`
and the two claim entries `data/claims/2026-10-30-musk-x-telepathy-bandwidth.toml` and
`data/claims/2026-10-30-musk-x-blindsight-ready.toml`. The format follows the sourcing pass of
2026-10-17 (`docs/verify-pass-2026-10-17.md`): every page opened is listed with its address and the
date it was read, and what it gave. A search tool's own summary was never taken as a source; a fact
was taken only from a page opened and read. Pages that refused an automated reader are listed and
were not got round. No stage, count or figure on the tree changed.

## The two posts

Read on 2026-10-31 through a public mirror of X's post data, `api.fxtwitter.com/elonmusk/status/<id>`,
which returns a post's text, its time to the second, its id and the post it quotes. No session of
this project can open x.com itself. The claims log's 2020 Musk entry was read from X's own embed data
for the post, which is the same kind of public copy.

- `https://api.fxtwitter.com/elonmusk/status/2116019939056513218` (read 2026-10-31): the Blindsight
  post, 2026-10-30 04:10:41 universal time (21:10 Pacific on 2026-10-29). Text, word for word: "Our
  second product is called Blindsight and it will, as the name suggests, enable even those who are
  completely blind or have never seen to see. / It is ready from an engineering standpoint. Just
  waiting on regulatory approval." The mirror gives its quoted post as
  `https://x.com/elonmusk/status/2116018780111597911`, 2026-10-30 04:06:05 universal time: "Neuralink's
  first product is called Telepathy. / It enables high-speed communication with computers or humans
  simply by thinking. Output bandwidth will vastly exceed the fastest human speech or typing in a few
  years. Read that sentence again." The brief gave the quoted post's id with its last digits unsure;
  the mirror settled it as 2116018780111597911.
- Both addresses on x.com answered a plain request with status 200 on 2026-10-31, so a reader can
  open them in a browser; the text was not read from those pages.

## Neuralink's own publications

The company's pages are built by scripts: a plain fetch of the home page, the trials page and the
newest updates returns a shell, and the newest updates' text sits in a shadow document that the
built-in browser can read with a script. Every page below was read in the built-in browser on
2026-10-31 unless it says otherwise.

- `https://neuralink.com/` (home page): "Our brain-computer interface translates neural signals into
  actions. In our clinical trials, people are using Neuralink devices to control computers and
  robotic arms with their thoughts. This technology will restore autonomy to those with unmet medical
  needs and unlock new dimensions of human potential." Five named participants with implant months
  (January 2024 to April 2025). Nothing about Blindsight, Telepathy by name, bandwidth or merging.
- `https://neuralink.com/updates/` (the list of every update, with dates): 50 items from the July
  2019 launch event to 2026-10-29. Items used: "Two Years of Telepathy" (2026-01-28), "Pretraining on
  50,000 Hours of Unlabeled Brain Data" (2026-10-01), "A 72-Hour Engineering Sprint for Translating
  Thought to Speech" (2026-10-29), "Real-Time Communication Restoration in ALS with a Fully
  Implanted Speech Brain-Computer Interface" (2026-10-23, an outside link to Muscle & Nerve), "The
  curse of dimensionality in motor cortex" (2026-01-26, bioRxiv), "GB-PRIME Study Launch"
  (2025-07-31), "CAN-PRIME Study Launch" (2024-11-20), "Neuralink Receives Breakthrough Device
  Designation for Blindsight" (2024-09-17), "A Year of Telepathy" (2025-02-05), "Neuralink's
  First-in-Human Clinical Trial is Open for Recruitment" (2023-09-19). The list has no post about
  the 2026-10-30 claims and no post naming Blindsight after 2024-09-17.
- `https://neuralink.com/trials/` (the address `/blindsight/` redirects here): two "Active trial"
  cards, "Control devices with your mind" and "Communicate with your thoughts"; a link "View our
  studies on ClinicalTrials.gov"; no card for sight. Footer line: "Neuralink devices are
  investigational and have not been approved by the FDA or other regulatory authorities." The
  address `https://neuralink.com/telepathy/` returns 404.
- `https://neuralink.com/updates/two-years-of-telepathy/` (2026-01-28): "Our first product,
  Telepathy, aims to enable people with paralysis to directly control computers, phones, and robotic
  limbs using their thoughts alone." "With a growing crew of 21 Neuralnauts enrolled in trials
  worldwide". "Using a computer mouse with their hands, able-bodied people transmit around 8-10 bits
  per second on average ... Nick achieved over 10 BPS within his first week". Typing by imagined
  finger movement "up to 40 words per minute"; the VOICE speech trial aims at "conversational
  speeds of 140 words per minute". "higher signal quality across 18 of the subsequent 20
  participants"; "our current record of zero serious device-related adverse events"; "from three
  participants in 2024 to multiple participants per month in 2025". Plans: 1,000 to 3,000
  electrodes; inserting threads through the dura.
- `https://neuralink.com/updates/pretraining-on-50000-hours/` (2026-10-01): "The median
  Neuralinker BPS is roughly 10"; "six participants reached personal records. Three surpassed our
  previous record of 10.39 BPS, and one reached 11.32 BPS — a new BCI record" (participant P15, on
  "standard" cursor control; a separate "cursor teleportation" experiment "crossed 10 BPS in initial
  testing"). Formula for BPS given (grid task; information per selection times net correct
  selections a minute over 60). Over 50,000 hours of neural data streamed since the trial began;
  first participant over 9,000 hours. Same footer disclaimer. No peer review; the post's
  references are to other groups' papers.
- `https://neuralink.com/updates/72-hour-voice-hackathon/` (2026-10-29): a 72-hour visit to a VOICE
  study participant's home; features built (voice activity detection from neural signals, a mobile
  app, dictation into a keyboard, phone-call integration). No rate, no count. Same disclaimer.
- `https://neuralink.com/updates/a-year-of-telepathy/` (2025-02-05): "It enables users to operate
  their phones and computers with just their thoughts, a capability we call 'Telepathy.'" "Today,
  there are three people with Telepathy: Noland, Alex, and Brad." Table of trials: PRIME
  (NCT06429735) and CONVOY (NCT06710626) in the United States, CAN-PRIME (NCT06700304) in Canada;
  "We do not have any active clinical investigations in the United Kingdom at the time of this post".
- `https://neuralink.com/updates/neuralink-receives-breakthrough-device-designation-for-blindsight/`
  (2024-09-17): the whole post is two sentences: "We have received Breakthrough Device Designation
  from the FDA for Blindsight, for individuals with vision impairment. Join us in our quest to bring
  back sight to those who have lost it."
- `https://neuralink.com/updates/gb-prime-study-launch/` (2025-07-31): "approvals from the Medicines
  and Healthcare products Regulatory Agency (MHRA), the Health Research Authority (HRA) and Health
  and Care Research Wales (HCRW), and the London – Camberwell St Giles Research Ethics Committee
  (REC)"; two sites, University College London Hospitals and Newcastle upon Tyne Hospitals.
- `https://neuralink.com/updates/can-prime-study-launch/` (2024-11-20): "approval from Health Canada
  to launch the CAN-PRIME Study, our first international trial".
- `https://neuralink.com/updates/first-clinical-trial-open-for-recruitment/` (2023-09-19): "The
  PRIME Study is being conducted under the investigational device exemption (IDE) awarded by the FDA
  in May 2023"; approval "from the reviewing independent institutional review board and our first
  hospital site to begin recruitment".
- `https://neuralink.com/updates/prime-study-progress-update-user-experience/` (2024-05-08): already
  the source of the bandwidth series' 8.0 bits a second point and the "engineers with a mouse (~10
  BPS)" baseline; fetched again on 2026-10-31 (status 200) and not re-read.

## Regulators and registries

- `https://www.fda.gov/medical-devices/how-study-and-market-your-device/breakthrough-devices-program`
  (read 2026-10-31, plain fetch): "The Breakthrough Devices Program is a voluntary program for
  certain medical devices and device-led combination products that provide for more effective
  treatment or diagnosis of life-threatening or irreversibly debilitating diseases or conditions."
  "intended to provide patients and health care providers with timely access to medical devices by
  speeding up development, assessment, and review for premarket approval, 510(k) clearance, and De
  Novo marketing authorization. Breakthrough Devices must meet the FDA's rigorous standards for
  device safety and effectiveness in order to be authorized for marketing." The FDA publishes no
  list of designated devices by name; the designation for Blindsight rests on the company's own
  announcement and the Reuters report below.
- ClinicalTrials.gov, read 2026-10-31 through the registry's own data service
  (`https://clinicaltrials.gov/api/v2/studies?query.spons=Neuralink`) and the search page
  `https://clinicaltrials.gov/search?spons=Neuralink` in the browser: seven studies sponsored by
  Neuralink, six recruiting and one enrolling by invitation, none with results posted, none for
  sight. PRIME NCT06429735 (United States; started 2024-01-09; 15 planned; Barrow Neurological
  Institute and the University of Miami; primary completion estimated June 2026, completion
  January 2031; last updated 2026-01-09). CAN-PRIME NCT06700304 (Canada; started 2024-11-20; 6
  planned). UAE-PRIME NCT06992596 (United Arab Emirates; Cleveland Clinic Abu Dhabi; started
  2025-05-09; 10 planned). GB-PRIME NCT07127172 (United Kingdom; started 2025-07-31; 7 planned;
  University College London Hospitals and Newcastle). CONVOY NCT06710626 (robotic arm; 3). VOICE
  NCT07224256 (speech; started 2025-10-03; 6). NCT07407725 (an outcome-assessment study; 60). The
  record's summaries describe the N1 implant and R1 robot; none states a rate or a patient count
  reached.
- Health Canada's own site and the United Kingdom regulator's site were opened only to check the
  links the post makes at the names' first mention (`https://www.canada.ca/en/health-canada.html`
  and `https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency`,
  both 2026-10-31). Neither carries a Neuralink notice that was found; the approvals rest on
  Neuralink's own announcements and the registry.

## Peer-reviewed and preprint reports

- Crossref's record for DOI 10.1002/mus.70436 (`https://api.crossref.org/works/10.1002/mus.70436`,
  read 2026-10-31) and the journal page `https://onlinelibrary.wiley.com/doi/10.1002/mus.70436`
  (opened in the browser 2026-10-31; a plain fetch is refused): "Proceedings of the 25th Annual
  Meeting of the Northeast ALS Consortium", Muscle & Nerve volume 74, supplement S2, pages S1 to
  S112, published 2026-10-23. It is a supplement of meeting abstracts, and Neuralink's updates page
  links to it as "Early Neuralink speech restoration data shared during the 25th Annual Meeting of
  the Northeast ALS Consortium". The abstract itself was not read (the supplement is one document
  of 112 pages behind the publisher's reader); the post calls it an abstract in a meeting's
  proceedings and not a full paper, which is what the record shows.
- The 2026-01-26 bioRxiv item linked from the updates page
  (`https://www.biorxiv.org/content/10.64898/2026.01.26.701668v1.full`): by its own summary on the
  updates page, about how estimates of the dimensionality of motor-cortex activity scale with the
  number of neurons recorded. Not opened; not a trial result; not cited in the post.
- Searches for a peer-reviewed report of a Neuralink participant (web search, 2026-10-31: "Neuralink
  peer-reviewed paper human participant PRIME results published journal preprint") found no
  publication. One result (PYMNTS, carrying Bloomberg) said Neuralink had sent a paper on its first
  three patients to the New England Journal of Medicine; the page that carried it
  (`https://www.healthleadersmedia.com/innovation/musks-neuralink-submits-brain-implant-patient-data-nejm`)
  refused a plain fetch (403) and was not opened, so the submission is not stated in the post. The
  post says only that no peer-reviewed report was found, which is what the search showed.

## Coverage opened

- `https://arc-dev.theglobeandmail.com/business/international-business/article-musks-neuralink-gets-fdas-breakthrough-device-tag-for-blindsight`
  (read 2026-10-31 by the fetch agent; the Reuters address
  `https://www.reuters.com/business/healthcare-pharmaceuticals/musks-neuralink-receives-fdas-breakthrough-device-tag-brain-implant-2024-09-17/`
  refuses automated readers): the Reuters report of 2024-09-17 as carried by The Globe and Mail.
  "The experimental device, known as Blindsight, 'will enable even those who have lost both eyes
  and their optic nerve to see,' Musk said in a post on X." "The FDA's breakthrough tag is given to
  certain medical devices that provide treatment or diagnosis of life-threatening conditions. It is
  aimed at speeding up development and review of devices currently under development." "Neuralink
  did not immediately respond to a request seeking details about when it expects the Blindsight
  device to move into human trials."
- `https://www.mobihealthnews.com/news/elon-musk-provides-update-blindsight-implant-trials` (read
  2026-10-31 in the browser; a plain fetch is refused): Jessica Hagen, 2025-06-23. Musk at a Y
  Combinator event: "In the next six to 12 months, we'll be doing our first implants for vision,
  where, even if somebody is completely blind, we can write directly to the visual cortex, and
  we've had that working in monkeys. Actually, I think one of our monkeys now has had the visual
  implant for three years". Also: "The sustained output of a human over the course of a day is less
  than 1 bit per second." The article says the implant had then been in five people. No recording
  of the event was reached, so this is held as coverage, not entered as a claim.
- `https://www.aol.com/news/neuralink-targets-1-billion-revenue-220503712.html` (read 2026-10-31 by
  the fetch agent): the Reuters item of 2025-07-23 on Bloomberg's report from investor documents,
  "Neuralink targets $1 billion revenue by 2031, Bloomberg News reports". "By 2030, Neuralink
  anticipates launching Blindsight, expanding surgeries to 10,000 per year and generating over $500
  million in revenue." The Reuters and Bloomberg pages themselves were not opened.
- `https://en.wikipedia.org/wiki/Blindsight_(Neuralink)` (read 2026-10-31, plain fetch): a stub,
  last edited 2026-10-26; cites Reuters, the Economic Times, Silicon Republic, Interesting
  Engineering, the New York Post and Business Insider for the 2024 designation and the purpose. No
  first implant is reported.

## Pages that refused, and leads not followed

- University College London Hospitals' release on the first British implant
  (`https://www.uclh.nhs.uk/news/first-uk-patient-receive-neuralink-implant-uses-computer-just-using-his-thoughts`):
  a bot check in both a plain fetch and the browser; left alone. Sky News's article of 2026-01-29,
  linked from Neuralink's updates page: refused (403). So the post says nothing about the first
  British patient beyond the regulator's approval and the registry entry.
- MobiHealthNews's 2025-04-01 piece on a Wisconsin town hall (a first Blindsight implant "by the end
  of 2025"), and the business press on the same remark: refused or not opened; not stated in the
  post or the claims.
- Musk's own X post of 2024-09-17 thanking the FDA, and Neuralink's post of the same day on X: their
  ids were not found in any page opened, so they were not pulled through the mirror. Neuralink's own
  site post of that day is the source used.
- The Lex Fridman episode 438 remark on symbiosis and the Y Combinator recording of June 2025: not
  pulled; the log's not-entered list already carries the first.

## What the record shows, product by product

**Telepathy.** The company's name for its implant's use in trials: cursor, phone and robotic-arm
control, and typing by imagined finger movement, in people with paralysis. 21 people enrolled
worldwide as of 2026-01-28 (the company's count; no later company count found). Permissions: an
investigational device exemption in the United States (May 2023), Health Canada (November 2024),
the MHRA and ethics bodies in Great Britain (July 2025), and a trial in the United Arab Emirates
(from May 2025, per the registry; no regulator's notice found). No regulator has approved the
device for sale, by the company's own footer. Rates, all the company's own and none peer reviewed:
11.32 bits a second for one participant on the grid task (2026-10-01), median roughly 10, typing up
to 40 words a minute (2026-01-28). The gap to the claim: speech carries about 39 bits a second
(Coupé and colleagues 2019, in the bandwidth series), an advanced typist about 120 words a minute,
which Zheng and Meister put at about 10 bits a second (2024, in the series); the company's cursor
figure would have to more than triple and its typing figure triple, and be measured checkably. The
tree's own upgrade for this asks for above 40 bits a second over ten minutes in a peer-reviewed
report (`link-brain-link-carries-more-information-than-speech`, idea only).

**Blindsight.** An implant for the visual cortex. The record: a Breakthrough Device designation
from the FDA announced 2024-09-17 (not an approval; not permission to implant); no trial on the
company's trials page or in the United States registry; no person known to have it; the company's
July 2025 investor documents, per Bloomberg via Reuters, anticipated a launch by 2030; Musk's June
2025 window of six to twelve months passed. The leaf
`senses-implant-in-the-visual-cortex-gives-sight-without-eyes` is at first human since 1968
(Brindley and Lewin), its next stage needs a regulator's approval record, and its record holds no
report of a person blind from birth seeing through such an implant.

**Not found.** A company count of participants later than 21 (January 2026); any peer-reviewed
report of a Neuralink participant; any regulator's own notice of the Blindsight designation or of a
trial permission for it; the ids of the September 2024 X posts.

## What the post may quote

Followed from the site's existing practice (the claims page: at most one short phrase per claim, in
quotation marks, exactly as in the source; the news posts: short attributed quotations with a link)
and the brief:

- Neuralink's own posts and pages: short phrases with attribution and a link, under about 25 words
  each, a handful in a post. The post quotes six: the Telepathy description (2026-01-28), the
  investigational footer, "roughly 10" (2026-10-01), the Blindsight designation sentence
  (2024-09-17), and two phrases from the FDA's program page. Nothing is reproduced at length.
- Musk's two posts of 2026-10-30: quoted in full in the news post, because they are short public
  statements (four sentences and three) and the claims log's method is to keep the exact words; the
  log entries themselves keep one phrase each, under the 25-word rule.
- Coverage: one sentence from the Reuters report (Musk's words as it quoted them), one from
  MobiHealthNews (Musk's words at the June 2025 event), one from the Reuters item on Bloomberg's
  report. Each attributed and linked.

## Voice run sheet, on the post

The reply run sheet (`calibration-problem/editorial/vcp-reply-runsheet.md`, stamped master 2026-10-12)
was run on 2026-10-31. The master copy in `calibration-problem/editorial/` is stamped 2026-10-12 and
ends at Pattern 27; a working copy in one of that repository's worktrees (stamped 2026-10-18) adds
Pattern 28, the missing joint (keep the connecting words; ruled 2026-10-21). No copy found carries a
Pattern 29, so the rule the brief states for it (an example must not borrow its conclusion) was
applied as stated.

- Pass 0: every figure in the post carries a link to the page it came from; the one negative ("I
  looked for one and found none") is owned. Links were opened: every outside address answered 200
  to a plain fetch or opened in the browser (the publishers' pages for three papers, MobiHealthNews,
  Bloomberg's and Reuters' home pages refuse plain fetches and opened in the browser; one dead link,
  a Wikipedia page for Christophe Coupé that does not exist, was removed).
- Pass 1: no flagged word; no economy metaphor. Every outside name has an identifying phrase at
  first mention (Pattern 27): Musk, Neuralink, X, the FDA, Health Canada, the MHRA, Coupé and
  colleagues, Zheng and Meister, Reuters, Bloomberg, Brindley and Lewin.
- Pass 2: no em dash. Contrastive pairs cut to one that carries the point ("A breakthrough
  designation is not an approval"); the trials sentence was rewritten to let the company's own
  footer carry the contrast. Two signposts removed ("so here are the numbers"; "Now the
  yardsticks"). The one-word paragraph "Nothing." became a sentence. "Median" glossed as the middle
  participant's rate; "bits a second", "peer-reviewed", "investigational device exemption" and
  "Breakthrough Device designation" each explained in plain words at first use (Pattern 14).
  Connecting words kept in the three-step sentences (Pattern 28). No example borrows its
  conclusion (Pattern 29 as stated in the brief).
- Pass 3: read for speech-making; the closing paragraph states the count and the log entries and
  stops.
- Dates in the post's prose are written "October 30th, 2026", as the brief asked; the two earlier
  posts write "18 October 2026". John may want one form across the news section.
