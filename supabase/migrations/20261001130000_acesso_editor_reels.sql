-- Aplicada no projeto reels-editor (eteolienohxnxojacqec) em 01/10/2026 pelo MCP do Supabase.
-- Editor-reels: quem pode usar as APIs (domínios de e-mail) e registro de uso.
-- As tabelas ficam fechadas para anon/authenticated: só a Edge Function (service role) e o hook de cadastro leem.

create table public.dominios_permitidos (
  dominio text primary key check (dominio = lower(dominio)),
  observacao text,
  criado_em timestamptz not null default now()
);

create table public.acessos_bloqueados (
  email text primary key check (email = lower(email)),
  motivo text,
  criado_em timestamptz not null default now()
);

create table public.uso_api (
  id bigint generated always as identity primary key,
  user_id uuid not null,
  email text not null,
  servico text not null,
  consulta text,
  resultados int,
  criado_em timestamptz not null default now()
);
create index uso_api_user_criado_idx on public.uso_api (user_id, criado_em desc);

alter table public.dominios_permitidos enable row level security;
alter table public.acessos_bloqueados enable row level security;
alter table public.uso_api enable row level security;

revoke all on public.dominios_permitidos, public.acessos_bloqueados, public.uso_api from anon, authenticated, public;

insert into public.dominios_permitidos (dominio, observacao) values ('liv.law', 'LIV Immigration Law');

create or replace function public.hook_cadastro_por_dominio(event jsonb)
returns jsonb
language plpgsql
set search_path = ''
as $$
declare
  dominio text := lower(split_part(event->'user'->>'email', '@', 2));
begin
  if exists (select 1 from public.dominios_permitidos d where d.dominio = dominio) then
    return '{}'::jsonb;
  end if;
  return jsonb_build_object('error', jsonb_build_object(
    'message', 'Use o e-mail da empresa para acessar o editor.', 'http_code', 403));
end;
$$;

grant usage on schema public to supabase_auth_admin;
grant select on public.dominios_permitidos to supabase_auth_admin;
grant execute on function public.hook_cadastro_por_dominio(jsonb) to supabase_auth_admin;
revoke execute on function public.hook_cadastro_por_dominio(jsonb) from authenticated, anon, public;

-- 01/10/2026: usuários da Imigrar também
insert into public.dominios_permitidos (dominio, observacao) values ('imigrareua.com', 'Imigrar EUA') on conflict do nothing;
