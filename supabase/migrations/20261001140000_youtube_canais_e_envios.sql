-- Aplicada no projeto reels-editor em 01/10/2026 pelo MCP do Supabase.
-- Envio de shorts pro YouTube pelo servidor do editor. A autorização (refresh token) de cada canal fica no Vault.

create table public.administradores (
  email text primary key check (email = lower(email)),
  criado_em timestamptz not null default now()
);
insert into public.administradores (email) values ('dev@liv.law');

create table public.youtube_canais (
  canal text primary key check (canal ~ '^[a-z0-9_-]+$'),
  nome text,
  segredo_id uuid not null,
  conectado_por text not null,
  conectado_em timestamptz not null default now()
);

create table public.youtube_envios (
  id bigint generated always as identity primary key,
  canal text not null references public.youtube_canais(canal),
  user_id uuid not null,
  email text not null,
  titulo text not null,
  publicar_em timestamptz,
  video_id text,
  status text not null default 'iniciado',
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);
create index youtube_envios_criado_idx on public.youtube_envios (criado_em desc);

alter table public.administradores enable row level security;
alter table public.youtube_canais enable row level security;
alter table public.youtube_envios enable row level security;
revoke all on public.administradores, public.youtube_canais, public.youtube_envios from anon, authenticated, public;

create or replace function public.yt_salvar_token(p_canal text, p_nome text, p_token text, p_email text)
returns void language plpgsql security definer set search_path = '' as $$
declare v_id uuid;
begin
  select segredo_id into v_id from public.youtube_canais where canal = p_canal;
  if v_id is null then
    v_id := vault.create_secret(p_token, 'youtube_' || p_canal, 'refresh token do canal ' || p_canal);
  else
    perform vault.update_secret(v_id, p_token);
  end if;
  insert into public.youtube_canais (canal, nome, segredo_id, conectado_por)
  values (p_canal, p_nome, v_id, p_email)
  on conflict (canal) do update set nome = excluded.nome, conectado_por = excluded.conectado_por, conectado_em = now();
end; $$;

create or replace function public.yt_ler_token(p_canal text)
returns text language sql security definer set search_path = '' as $$
  select s.decrypted_secret from public.youtube_canais c
  join vault.decrypted_secrets s on s.id = c.segredo_id where c.canal = p_canal;
$$;

revoke execute on function public.yt_salvar_token(text, text, text, text) from public, anon, authenticated;
revoke execute on function public.yt_ler_token(text) from public, anon, authenticated;
grant execute on function public.yt_salvar_token(text, text, text, text) to service_role;
grant execute on function public.yt_ler_token(text) to service_role;
