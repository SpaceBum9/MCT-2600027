import { createServerFn } from "@tanstack/react-start";
import { getSql } from "@/lib/db";
import { DEPARTMENTS, type DepartmentId } from "./catalog";
import {
  emptyAlignment,
  meanAlignment,
  trainSession,
  type Alignment,
  type Round,
} from "./agents";

function asAlignment(rows: { department: string; score: number }[]): Alignment {
  const base = emptyAlignment();
  for (const row of rows) {
    if (row.department in base) base[row.department as DepartmentId] = row.score;
  }
  return base;
}

export const loadAcademy = createServerFn({ method: "GET" }).handler(async () => {
  const sql = await getSql();
  const scores = await sql<{ department: string; score: number }>`
    select department, score from cmd_alignment
  `;
  const rounds = await sql<{
    id: number;
    game: string;
    department: string;
    ok: boolean;
    teacher: string;
    learner: string;
    challenger: string;
    referee: string;
    createdAt: string;
  }>`
    select id, game, department, ok, teacher, learner, challenger, referee,
           created_at as "createdAt"
    from cmd_rounds
    order by id desc
    limit 16
  `;
  const alignment = asAlignment(scores);
  return { alignment, mean: meanAlignment(alignment), rounds };
});

export const runTraining = createServerFn({ method: "POST" })
  .validator((input: { seed?: number; rounds?: number }) => ({
    seed: Number(input?.seed ?? Date.now() % 1_000_000),
    rounds: Math.min(20, Math.max(5, Number(input?.rounds ?? 8))),
  }))
  .handler(async ({ data }) => {
    const sql = await getSql();
    const scores = await sql<{ department: string; score: number }>`
      select department, score from cmd_alignment
    `;
    const trained = trainSession(asAlignment(scores), data.seed, data.rounds);
    for (const [department, score] of Object.entries(trained.alignment)) {
      await sql`
        insert into cmd_alignment (department, score)
        values (${department}, ${score})
        on conflict (department) do update set score = ${score}, updated_at = now()
      `;
    }
    for (const round of trained.log) {
      await sql`
        insert into cmd_rounds (game, department, ok, teacher, learner, challenger, referee)
        values (
          ${round.game},
          ${round.department},
          ${round.ok},
          ${round.teacher},
          ${round.learner},
          ${round.challenger},
          ${round.referee}
        )
      `;
    }
    return trained;
  });
