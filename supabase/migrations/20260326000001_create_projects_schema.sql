-- Create projects table
create table projects (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  status text default 'draft' check (status in ('draft', 'transcribed', 'translated', 'dubbed'))
);

-- Create audio_files table
create table audio_files (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references projects(id) on delete cascade not null,
  file_url text not null,
  original_filename text not null,
  duration real,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create transcriptions table
create table transcriptions (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references projects(id) on delete cascade not null,
  segments_json jsonb not null,
  language text not null,
  model text not null,
  options_json jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create translations table
create table translations (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references projects(id) on delete cascade not null,
  segments_json jsonb not null,
  target_language text not null,
  source_language text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create dubs table
create table dubs (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references projects(id) on delete cascade not null,
  audio_url text not null,
  voice_map_json jsonb not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create indexes for better performance
create index audio_files_project_id_idx on audio_files(project_id);
create index transcriptions_project_id_idx on transcriptions(project_id);
create index translations_project_id_idx on translations(project_id);
create index dubs_project_id_idx on dubs(project_id);

-- Enable Row Level Security (RLS) - for now, allow all operations
alter table projects enable row level security;
alter table audio_files enable row level security;
alter table transcriptions enable row level security;
alter table translations enable row level security;
alter table dubs enable row level security;

-- Create policies to allow all operations (adjust later for auth)
create policy "Allow all operations on projects" on projects for all using (true) with check (true);
create policy "Allow all operations on audio_files" on audio_files for all using (true) with check (true);
create policy "Allow all operations on transcriptions" on transcriptions for all using (true) with check (true);
create policy "Allow all operations on translations" on translations for all using (true) with check (true);
create policy "Allow all operations on dubs" on dubs for all using (true) with check (true);

-- Create function to update updated_at timestamp
create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = timezone('utc'::text, now());
  return new;
end;
$$ language plpgsql;

-- Create trigger to auto-update updated_at on projects
create trigger update_projects_updated_at
  before update on projects
  for each row
  execute function update_updated_at_column();
