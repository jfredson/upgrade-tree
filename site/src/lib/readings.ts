// Typed access to the weekly reading records the export script writes (scripts/export.py,
// docs/weekly-reading.md), plus the wording the pages share. Like tree.json, the file is
// generated at build time and is not committed; run `npm run export` to create it.
//
// Copied in shape from The Belt Equation's site/src/lib/scans.ts on 2026-10-16 (the tracker
// pattern's section 7.1: copy with a comment saying where it came from). A reading is one
// week's check of every upgrade against the news: for each upgrade read, what was searched,
// what was found, and one of four verdicts. The reading page shows every reading, the home
// page shows a line about the latest one, and each upgrade page shows its last three.
import readingsJson from '../data/readings.json';

export type Verdict = 'quiet' | 'noted' | 'stage-change' | 'flagged';

export type ReadingItem = {
  upgrade: string;
  upgrade_name: string;
  branch: string;
  branch_name: string;
  path: string;
  verdict: Verdict;
  queries: string[];
  found: string;
  sources: string[];
  moved_from: string | null;
  moved_to: string | null;
  moved_from_label: string | null;
  moved_to_label: string | null;
  for_john: string | null;
  /** On a flagged item: what took it off John's list and when; null while it is still waiting. */
  picked_up: { on: string; how: string } | null;
};

export type Reading = {
  date: string;
  ran_at: string;
  scope: 'weekly' | 'monthly';
  upgrades_read: number;
  searches: number;
  commit_before: string;
  by: 'hand' | 'scheduled';
  /** True on a hand-made fixture that stands in for a real week. The site says so wherever it shows one. */
  test: boolean;
  file: string;
  counts: Record<Verdict, number>;
  items: ReadingItem[];
};

/** One upgrade's own reading, as the upgrade page shows it: the run it came from, flattened in. */
export type UpgradeReading = {
  date: string;
  scope: Reading['scope'];
  by: Reading['by'];
  test: boolean;
  file: string;
  verdict: Verdict;
  found: string;
  sources: string[];
  moved_from_label: string | null;
  moved_to_label: string | null;
  for_john: string | null;
  picked_up: { on: string; how: string } | null;
};

export type WaitingItem = ReadingItem & { reading_date: string; reading_file: string; test: boolean };

export type Readings = {
  exported_on: string;
  readings: Reading[];
  waiting_on_john: WaitingItem[];
  by_upgrade: Record<string, UpgradeReading[]>;
  counts: {
    readings: number;
    real_readings: number;
    test_readings: number;
    items: number;
    waiting_on_john: number;
  };
};

export const readings = readingsJson as unknown as Readings;

/** The most recent reading, or null before the first one has run. */
export const latestReading: Reading | null = readings.readings[0] ?? null;

/** Every reading of one upgrade, newest first. */
export const readingsFor = (upgradeId: string): UpgradeReading[] => readings.by_upgrade[upgradeId] ?? [];

/** The badge on a card: what the reading decided, in two or three words. */
export const verdictLabel: Record<Verdict, string> = {
  quiet: 'Nothing new',
  noted: 'No change',
  'stage-change': 'A stage moved',
  flagged: 'Waiting on me',
};

/** The same four, in a sentence, for the key on the reading page and the upgrade pages. */
export const verdictMeaning: Record<Verdict, string> = {
  quiet: 'Nothing about this upgrade turned up in the search results for the week. The search tool cannot limit results by date, so this means nothing was found, not that nothing happened.',
  noted: 'Something relevant, dated in the week or new to the record, turned up and it did not meet the test for the next stage, so nothing changed.',
  'stage-change': 'The next stage was reached, on a record of the kind the upgrade itself names, and the reading moved it one stage.',
  flagged: 'Something the reading is not allowed to do on its own, written up for me to rule on.',
};

export const scopeLabel: Record<Reading['scope'], string> = {
  weekly: 'every upgrade with a stage still to reach',
  monthly: 'every upgrade, including the ones already in wide use',
};

/** Counts read better as words at the low end: "none", "one", then digits. */
export function plainCount(n: number): string {
  return n === 0 ? 'none' : n === 1 ? 'one' : String(n);
}

/** The moment the reading finished, in John's own time zone (the record keeps universal time,
    and the reading's date is already a Pacific date). Formatted at build time. */
export function ranAtLabel(reading: Reading): string {
  const d = new Date(reading.ran_at);
  if (Number.isNaN(d.getTime())) return reading.ran_at;
  const time = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', hour: 'numeric', minute: '2-digit' }).format(d);
  const day = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Los_Angeles', year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);
  return `${time} Pacific, ${day}`;
}

/** "32 upgrades read, none moved" or "32 upgrades read, one moved and two left for me": the line
    the home page strip and the reading page both use, so the site says the same thing in both. */
export function readingSummary(reading: Reading): string {
  const read = `${reading.upgrades_read} upgrade${reading.upgrades_read === 1 ? '' : 's'} read`;
  const parts: string[] = [];
  const moved = reading.counts['stage-change'];
  parts.push(moved ? `${plainCount(moved)} moved` : 'none moved');
  if (reading.counts.flagged) {
    const open = reading.items.filter((i) => i.verdict === 'flagged' && !i.picked_up).length;
    parts.push(open ? `${plainCount(open)} left for me` : `${plainCount(reading.counts.flagged)} ruled on since`);
  }
  const joined = parts.length === 1 ? parts[0] : parts.slice(0, -1).join(', ') + ' and ' + parts[parts.length - 1];
  return `${read}, ${joined}`;
}
