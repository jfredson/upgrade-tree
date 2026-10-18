# The sourcing pass on the five open checks, 2026-10-17: searches and pages opened

Done on 2026-10-17 under John's rule of the same day: nothing in any public record rests on an AI
model's recollection; every fact carries a source a reader can open; a fact that cannot be sourced
after a real search leaves the record, with the reason in the changelog. Five checks were open
(the headline file said `to_verify: 5`). This is the log of what was searched and opened, with what
each page gave. Pages that refused an automated reader are listed too, and none was got round: the
two bot checks (the New England Journal of Medicine, DTIC's maintenance page) were left as they were.

A search tool's own summary was never taken as a source. A fact was taken only from a page opened and
read, and the page is named below.

## 1. Vidal 1977, a possible earlier first human (`data/link.toml`, scalp headset)

Searches:
- "Vidal 1977 Real-time detection of brain events in EEG Proceedings of the IEEE full text maze
  cursor" (web search): no copy of the paper; a differently titled 2008 paper by Schalk and others.
- "Vidal UCLA direct brain-computer communication ARPA final report DTIC visual evoked potentials
  maze cursor 1970s" (web search): pointed to two DTIC reports and to a 2011 review.

Pages and files opened:
- Crossref record for DOI 10.1109/PROC.1977.10542: title, 1977, no abstract, links to IEEE only.
- OpenAlex record for the same DOI: `is_oa: false`, no repository copy.
- Internet Archive search for the paper's title and for Vidal on "brain-computer": no hits.
- IEEE Xplore page for the paper (document 1454811): abstract and metadata read. The abstract speaks
  of detecting and classifying single evoked responses in real time, with each classification usable
  "in subject feedback"; it does not mention a maze or a cursor. Full text: "Sign In or Purchase".
- Annual Reviews page for Vidal's 1973 review (10.1146/annurev.bb.02.060173.001105), the open PDF
  read in full (24 pages, text layer): a proposed programme of experiments (no result of steering
  anything); the conclusion on page 178 says direct brain-computer communication "still lies
  somewhat in the future".
- DTIC report AD-777 720, Vidal, "Biocybernetic Control in Man-Machine Interaction", April 1974:
  DTIC's own address refused (403, then a maintenance page); a partial copy (the first megabyte, the
  rest cut off by the archive) from the Internet Archive was read as text. It reports colour-flash
  evoked-response experiments and mentions no maze or cursor in what was readable.
- DTIC report ADA026193 (semi-annual report, July 1975 to January 1976): not reachable (DTIC
  maintenance page; no archived copy).
- McFarland and Wolpaw, "Brain-computer interfaces for communication and control", Communications of
  the ACM 54(5), May 2011, pages 60 to 66 (open copy at neurotechcenter.org), read in full. Page 61:
  Vidal's 1970s system based on visual evoked potentials; users looking at a flashing checkerboard
  generated right, up, left and down commands "enabling them to move through a maze presented on a
  graphics terminal", trained a discriminant function and "navigated the maze online in real time";
  it cites the 1977 paper as its reference 34.

Outcome: the paper cannot be read. The question is parked: the record states what is and is not
known and the first-human date stays 1988. A decision task for John is on the roadmap.

## 2. The first mitochondrial-donation child's birth date (`data/inheritance.toml`)

Searches:
- "New Scientist 'World's first baby born with new "3 parent" technique' Zhang Mexico boy born
  6 April" (web search).
- "First live birth using human oocytes reconstituted by spindle nuclear transfer for mitochondrial
  DNA mutation causing Leigh syndrome Fertility and Sterility 2016 abstract" (web search).
- "'three-parent' baby Zhang New Hope Fertility Center boy 'was born on April 6'" (web search,
  extended).
- "'uneventful pregnancy with delivery of a healthy boy at 37 weeks of gestation' Leigh syndrome
  spindle nuclear transfer" (web search).

Pages opened:
- Pages searched for a birth date, none of which gave one in a form usable: Columbia Bioethics
  journal "It's a Boy" page, Duke Health Referring Physicians, KFF Health News, CBC (nothing found
  on the page as fetched), Gizmodo (only "five-month old"), bioethics.com's copy of the New Scientist
  opening (no birth date), the Guardian and MaltaToday (empty when fetched), PubMed (a challenge
  page, `203`).
- CNN 2016-09-27 ("A healthy baby boy was born on April 6 in Mexico"), CNN 2017-08-07 (restates it
  and quotes the paper), Science News (quoting New Scientist), CBS News ("As first reported in New
  Scientist, the baby was born on April 6, 2016"), New Hope Fertility Center's page for Dr Zhang
  ("born in April 2016", no day), NBC News (quotes the 2016 abstract: "currently 3 months old"),
  NPR 2017-04-08 (no birth date found on the page): press, all derived from the first report.
- The fertility society's 2016 abstract (Fertility and Sterility 106(3) supplement, e375-e376, DOI
  10.1016/j.fertnstert.2016.08.004): its page and the journal's site refused automated readers
  (ScienceDirect captcha, Cloudflare check); the abstract was not read.
- New Scientist, "Exclusive: World's first baby born with new '3 parent' technique", Jessica
  Hamzelou, 2016-09-27, opened in the browser pane: in the box "Two women, one man and a baby", "the
  boy was born on 6 April 2016". The article is the first report, run with the clinic's cooperation
  (the clinic asked that the family's names be removed); "five-month-old" in its opening agrees.
- The 2017 paper (the first-human record) was read in full on 2026-10-16 by an earlier session and
  gives no birth date, only an age of seven months; it was not opened again today.

Outcome: confirmed, with the news report as the named source. No clinic or author document that can
be opened gives the day.

## 3. Which vocabulary the 78 words a minute belongs to (`data/bandwidth.toml`)

Pages and files opened:
- The journal's page for Metzger and others (Nature 620, 1037, 10.1038/s41586-023-06443-4), open
  access: abstract and extended-data legends.
- The PubMed Central full text (PMC10826467, fetched through the NCBI efetch service as XML): the
  Results ("Text decoding"), the legend of Figure 2 and Methods read. The Results say the participant
  silently attempted 249 randomly selected sentences from the "1024-word-General" set, not used in
  training, and give a median word error rate of 25.5 per cent and a median real-time rate of 78.3
  words a minute; the legend of Figure 2 says panels b to g "were computed using the real-time
  evaluation trials with the 1024-word-General sentence set".

Outcome: confirmed, with the wording tightened (see the changelog).

## 4. The UC Davis speech decoder's date (`data/bandwidth.toml`)

Searches:
- "UC Davis Health 'An Accurate and Rapidly Calibrating Speech Neuroprosthesis' NEJM published
  August 14, 2024" (web search).
- "health.ucdavis.edu news 'New brain-computer interface allows man with ALS to speak again' ..."
  (web search restricted to the university and journal domains).

Pages opened:
- Crossref record (10.1056/NEJMoa2314132): print date 2024-08-15; record created 2024-08-14.
- PubMed through the NCBI services (PMID 39141853): print date 2024-08-15; record entered
  2024-08-14; PubMed Central released the author copy on 2024-08-16.
- Europe PMC search record: print date 2024-08-01 month-level, record created 2024-08-14.
- The journal's own page (nejm.org): bot check, not got round.
- UC Davis Health news release, 2024-08-14 (health.ucdavis.edu), the university's page
  (ucdavis.edu/news) and ScienceDaily's copy: "A study about this work was published today in the New
  England Journal of Medicine", each dated 2024-08-14.

Outcome: corrected to 2024-08-14.

## 5. The Dubai 2017 account (`data/claims/2017-02-13-musk-world-governments-summit.toml`)

- The recording's automatic captions fetched again with yt-dlp: 26:54 to 26:59, "maybe do I don't
  know 10 bits per second or 100 if you being generous" (the captions drop the "'re"). The earlier
  Whisper reading, recorded in the claim on 2026-10-17, has the same words.
- The record of John's ruling of 2026-10-17: the changelog, the record layout, the checking note, the
  TimeAssembler worklog entries of that day and the roadmap task that lists the Dubai account as the
  third item of the quoted-recordings decision (marked done after "yes to all"). None states in so
  many words which way he answered on the wording; the account was brought to what the transcripts
  say, which the task sets against it, and the changelog says so.
