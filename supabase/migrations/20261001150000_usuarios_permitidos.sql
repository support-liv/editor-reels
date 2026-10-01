-- Aplicada no projeto reels-editor em 01/10/2026. Acesso nominal: domínio permitido E e-mail na lista (ou administrador).
create table public.usuarios_permitidos (
  email text primary key check (email = lower(email)),
  criado_em timestamptz not null default now()
);
alter table public.usuarios_permitidos enable row level security;
revoke all on public.usuarios_permitidos from anon, authenticated, public;
grant select on public.usuarios_permitidos, public.administradores to supabase_auth_admin;

insert into public.usuarios_permitidos (email) values
  ('dev@liv.law'), ('marketing@liv.law'), ('lara.freire@liv.law'), ('mariana.avila@liv.law'),
  ('liandra@imigrareua.com'), ('juan.rocha@imigrareua.com'), ('bruna.souza@imigrareua.com');

create or replace function public.hook_cadastro_por_dominio(event jsonb)
returns jsonb language plpgsql set search_path = '' as $$
declare
  v_email text := lower(event->'user'->>'email');
  v_dominio text := split_part(v_email, '@', 2);
begin
  if exists (select 1 from public.dominios_permitidos d where d.dominio = v_dominio)
     and (exists (select 1 from public.usuarios_permitidos u where u.email = v_email)
          or exists (select 1 from public.administradores a where a.email = v_email)) then
    return '{}'::jsonb;
  end if;
  return jsonb_build_object('error', jsonb_build_object(
    'message', 'Este e-mail não está liberado para o editor. Fale com o administrador.', 'http_code', 403));
end; $$;
