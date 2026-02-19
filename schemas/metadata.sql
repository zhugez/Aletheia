-- Core metadata schema (MVP)

create table if not exists sources (
  id uuid primary key,
  source_type text not null, -- book, paper, report
  title text not null,
  authors text,
  isbn text,
  doi text,
  language text,
  published_year int,
  domain text,
  license text,
  evidence_level text,
  created_at timestamptz default now()
);

create table if not exists chunks (
  id uuid primary key,
  source_id uuid not null references sources(id) on delete cascade,
  chapter text,
  section text,
  page_start int,
  page_end int,
  chunk_index int not null,
  text_content text not null,
  token_count int,
  created_at timestamptz default now()
);

create index if not exists idx_chunks_source on chunks(source_id);
