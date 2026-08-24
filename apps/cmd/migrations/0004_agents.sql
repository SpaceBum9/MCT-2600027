create table if not exists cmd_alignment (
  department text primary key,
  score      double precision not null,
  updated_at timestamptz not null default now()
);

create table if not exists cmd_rounds (
  id         serial primary key,
  game       text not null,
  department text not null,
  ok         boolean not null,
  teacher    text not null,
  learner    text not null,
  challenger text not null,
  referee    text not null,
  created_at timestamptz not null default now()
);
create index if not exists cmd_rounds_created_idx on cmd_rounds (created_at desc);
