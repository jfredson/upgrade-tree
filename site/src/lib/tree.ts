// Typed access to the JSON the export script writes (scripts/export.py), plus the small
// helpers the pages share. The JSON files are generated at build time and are not
// committed; run `npm run export` (or any build) to create them.
import treeJson from '../data/tree.json';
import changelogJson from '../data/changelog.json';

export const REPO = 'https://github.com/jfredson/upgrade-tree';

export type StageKey = 'idea-only' | 'shown-in-animals' | 'first-human' | 'in-clinical-use' | 'in-wide-use';

export type Stage = { key: StageKey; label: string; meaning: string; rank: number };

export type Ref = { id: string; name: string; path: string; stage: StageKey; stage_label: string };

export type Branch = {
  key: string;
  order: number;
  name: string;
  tagline: string;
  meaning: string;
  figure_region: string;
  path: string;
  count: number;
  counts_by_stage: Record<StageKey, number>;
  furthest_rank: number | null;
  furthest_stage: StageKey | null;
  furthest_label: string | null;
  first_human_or_beyond: number;
  upgrades: Ref[];
};

export type Rung = {
  key: StageKey;
  label: string;
  reached: boolean;
  current: boolean;
  reached_on: string | null;
  record: string | null;
};

export type Revision = { date: string | null; field: string | null; old: unknown; new: unknown; why: string | null };

export type Upgrade = {
  id: string;
  name: string;
  branch: string;
  branch_name: string;
  path: string;
  description: string;
  resolution: string;
  source: string;
  horizon: 'leaf' | 'mid' | 'root' | 'top';
  horizon_label: string;
  status: 'tracked' | 'withdrawn' | 'superseded';
  superseded_by: string | null;
  depends_on: string[];
  depends_on_refs: Ref[];
  needed_by: Ref[];
  stage: StageKey;
  stage_rank: number;
  stage_label: string;
  stage_reached_on: string | null;
  stage_record: string | null;
  ladder: Rung[];
  long_shot: boolean;
  mechanism: string | null;
  breaking_point: string | null;
  revisions: Revision[];
  verify: string[];
  /** Extra search terms for the weekly reading; a search aid only. */
  watch: string[];
  notes: string | null;
  example: boolean;
};

export type Tree = {
  exported_on: string;
  commit: string | null;
  headline_stage: StageKey;
  stages: Stage[];
  horizons: Record<string, string>;
  branches: Branch[];
  upgrades: Upgrade[];
  counts: {
    upgrades: number;
    first_human_or_beyond: number;
    by_stage: Record<StageKey, number>;
    long_shots: number;
    examples: number;
    branches_with_upgrades: number;
    to_verify: number;
  };
  /** The latest weekly reading, or null before the first one (scripts/export.py, export_readings). */
  last_checked: {
    date: string;
    scope: 'weekly' | 'monthly';
    by: 'hand' | 'scheduled';
    test: boolean;
    upgrades_read: number;
    moved: number;
    flagged: number;
    noted: number;
    flagged_waiting: number;
    movers: { id: string; name: string; path: string; moved_to_label: string | null }[];
  } | null;
};

export type Changelog = { source: string; intro: string; days: { date: string; items: string[] }[] };

export const tree = treeJson as Tree;
export const changelog = changelogJson as Changelog;

export const branchByKey = (key: string) => tree.branches.find((b) => b.key === key);
export const stageByKey = (key: StageKey) => tree.stages.find((s) => s.key === key)!;

export const statusLabel: Record<Upgrade['status'], string> = {
  tracked: 'Tracked',
  withdrawn: 'Withdrawn from use; the stage it reached stays on the record',
  superseded: 'Replaced by another entry',
};

/** "16 October 2026" from "2026-10-16". */
export function longDate(iso: string | null): string {
  if (!iso) return '';
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
}

export function hostOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

/** A link that opens a new issue in the public repository with a title and body filled in. */
export function issueUrl(title: string, body: string): string {
  return `${REPO}/issues/new?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`;
}
