# Servidor do time (Supabase)

As APIs externas do editor (hoje: B-roll do Pexels) passam por um servidor do time no Supabase
(projeto **reels-editor**). Assim ninguém precisa de chave de API no computador.

## Para quem usa
1. Uma vez por Mac: `python3 editor/conta.py entrar` → e-mail da empresa → código de 6 dígitos que chega no e-mail.
2. Pronto. A sessão fica no Chaveiro do macOS e se renova sozinha. `conta.py status` mostra quem está logado; `conta.py sair` apaga.
3. B-roll: `python3 editor/broll_api.py "airport crowd" --baixar 1`.

Só a palavra de busca sai do Mac. Vídeo de cliente nunca sobe.

## Como funciona
- `supabase/functions/broll`: confere o login, o domínio do e-mail (`dominios_permitidos`) e se a pessoa não está em
  `acessos_bloqueados`, limita a 300 buscas por dia, chama o Pexels com a chave guardada nos secrets e registra em `uso_api`.
- `public.hook_cadastro_por_dominio`: impede cadastro de e-mail fora dos domínios permitidos.
- `editor/supabase_config.json`: URL e chave *publishable* (pública por design; sozinha não acessa nada).

## Administração (no painel do Supabase ou SQL)
- Domínios liberados: `liv.law` e `imigrareua.com`. Liberar outro: `insert into dominios_permitidos (dominio) values ('exemplo.com');`
- Bloquear uma pessoa: `insert into acessos_bloqueados (email, motivo) values ('fulano@liv.law', 'saiu do time');`
- Ver uso: `select email, consulta, criado_em from uso_api order by criado_em desc limit 50;`
- Trocar a chave do Pexels: Edge Functions → Secrets → `PEXELS_API_KEY` (todo mundo passa a usar a nova na hora).
