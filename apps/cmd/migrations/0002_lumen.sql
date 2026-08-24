create table if not exists lumen_items (
  id         serial primary key,
  user_id    text not null,
  kind       text not null,
  title      text not null,
  source     text,
  result     text not null,
  created_at timestamptz not null default now()
);
create index if not exists lumen_items_user_id_idx on lumen_items (user_id, created_at desc);
