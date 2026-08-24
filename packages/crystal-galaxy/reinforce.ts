export const UP_FACTOR = 1.15;
export const DOWN_FACTOR = 0.75;
export const INITIAL_WEIGHT = 1;

export type Weighted = {
  key: string;
  title: string;
  body: string;
  source: string;
  weight: number;
  hits: number;
};

export type PulseRepo = {
  name: string;
  description: string;
  language: string | null;
  pushedAt: string;
  htmlUrl: string;
  openIssues: number;
  lastMessage: string | null;
};

export type HfPulse = {
  id: string;
  exists: boolean;
  runtime: string | null;
  likes: number | null;
  lastModified: string | null;
  url: string;
  note: string;
};

export function applyVote(weight: number, delta: 1 | -1) {
  const next = delta === 1 ? weight * UP_FACTOR : weight * DOWN_FACTOR;
  return Math.min(32, Math.max(0.05, next));
}

export function rankContext<T extends { weight: number; hits: number }>(items: T[], limit = 8) {
  return [...items]
    .sort((a, b) => b.weight - a.weight || b.hits - a.hits)
    .slice(0, limit);
}

export function formatWeight(w: number) {
  return w.toFixed(3);
}

export function buildAutomatedContext(items: Weighted[], limit = 6) {
  return rankContext(items, limit)
    .map(
      (c, i) =>
        `${i + 1}. [${formatWeight(c.weight)} · hits ${c.hits}] ${c.title} (${c.source})\n${c.body}`,
    )
    .join("\n\n");
}

export function buildLiveContext(opts: {
  crystals: Weighted[];
  pulse?: PulseRepo[];
  hf?: HfPulse | null;
  limit?: number;
}) {
  const crystals = buildAutomatedContext(opts.crystals, opts.limit ?? 6);
  const pulse = (opts.pulse ?? [])
    .slice(0, 4)
    .map((r) => {
      const msg = r.lastMessage ? ` — ${r.lastMessage}` : "";
      return `- ${r.name} (${r.language ?? "—"}) ${r.pushedAt}${msg}`;
    })
    .join("\n");
  const hf = opts.hf
    ? opts.hf.exists
      ? `- Hugging Face ${opts.hf.id} runtime=${opts.hf.runtime ?? "?"} likes=${opts.hf.likes ?? 0}`
      : `- Hugging Face ${opts.hf.id}: ${opts.hf.note}`
    : "";
  return [
    "AUTOMATED CONTEXT (schwerste Kristalle zuerst)",
    crystals,
    pulse ? `\nLIVE GITHUB PULS\n${pulse}` : "",
    hf ? `\nHUGGING FACE\n${hf}` : "",
  ]
    .filter(Boolean)
    .join("\n\n");
}

export function touchHit<T extends Weighted>(items: T[], key: string): T[] {
  return items.map((c) => (c.key === key ? { ...c, hits: c.hits + 1 } : c));
}

export function voteItem<T extends Weighted>(items: T[], key: string, delta: 1 | -1): T[] {
  return items.map((c) =>
    c.key === key ? { ...c, weight: applyVote(c.weight, delta), hits: c.hits + 1 } : c,
  );
}
