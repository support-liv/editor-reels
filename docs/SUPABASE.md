# Servidor do time (Supabase)

As APIs externas do editor (hoje: B-roll do Pexels) passam por um servidor do time no Supabase
(projeto **reels-editor**). Assim ninguém precisa de chave de API no computador.

## Para quem usa
1. Uma vez por computador (Mac ou Windows), o Claude roda `editor/conta.py entrar --email <email>` e a pessoa só clica no link que chega no e-mail.
   O e-mail sai pelo **SMTP próprio** (Office 365, remetente "Reels Editor LIV/Imigrar" <contato@imigrareua.com>; Authentication → Emails → SMTP), configurado e testado em 01/10/2026 — sem ele o Supabase só envia para membros do projeto. Pode cair no spam na primeira vez. Limite padrão ~30 e-mails de login/hora (Authentication → Rate Limits)
   (o link volta para `http://127.0.0.1:8723`, cadastrado em Auth → URL Configuration → Redirect URLs).
2. Pronto. A sessão fica no Chaveiro do macOS e se renova sozinha. `conta.py status` mostra quem está logado; `conta.py sair` apaga.
3. B-roll: `python3 editor/broll_api.py "airport crowd" --baixar 1`.

Só a palavra de busca sai do Mac. Vídeo de cliente nunca sobe.

## Como funciona
- `supabase/functions/broll`: confere o login, o domínio do e-mail (`dominios_permitidos`) e se a pessoa não está em
  `acessos_bloqueados`, limita a 300 buscas por dia, chama o Pexels com a chave guardada nos secrets e registra em `uso_api`.
- `public.hook_cadastro_por_dominio`: impede cadastro de e-mail fora dos domínios permitidos.
- `editor/supabase_config.json`: URL e chave *publishable* (pública por design; sozinha não acessa nada).

## Administração (no painel do Supabase ou SQL)
- Quem pode entrar: e-mail com domínio permitido **e** cadastrado em `usuarios_permitidos` (ou em `administradores`).
- Liberar uma pessoa: `insert into usuarios_permitidos (email) values ('nome@liv.law');`
- Tirar o acesso: `delete from usuarios_permitidos where email = 'nome@liv.law';` (e, se for urgente, `acessos_bloqueados`).
- Domínios liberados: `liv.law` e `imigrareua.com`. Liberar outro: `insert into dominios_permitidos (dominio) values ('exemplo.com');`
- Bloquear uma pessoa: `insert into acessos_bloqueados (email, motivo) values ('fulano@liv.law', 'saiu do time');`
- Ver uso: `select email, consulta, criado_em from uso_api order by criado_em desc limit 50;`
- Trocar a chave do Pexels: Edge Functions → Secrets → `PEXELS_API_KEY` (todo mundo passa a usar a nova na hora).

## YouTube (envio dos shorts)
- `supabase/functions/youtube`: conecta canais (só quem está em `administradores`) e abre a sessão de envio de cada vídeo.
  A autorização do canal fica no Vault (`youtube_canais` guarda só o id); o arquivo vai do Mac direto pro YouTube.
- Secrets: `YOUTUBE_CLIENT_ID` e `YOUTUBE_CLIENT_SECRET` (cliente OAuth do tipo **App para computador**).
- Tela de consentimento do Google em **Produção** (em "Teste" a autorização expira em 7 dias).
- Conectar um canal (uma vez): `python3 editor/youtube.py conectar --canal liv --nome "LIV Immigration Law"`.
- Enviar: `python3 editor/youtube.py lote projetos/<projeto>/publicacao.json --canal liv --inicio AAAA-MM-DD --hora 12:00`.
  Sobe como privado, com título, descrição, tags e (se pedido) o horário de publicação. Sem auditoria do Google, o canal
  pode ficar restrito a privado: aí alguém programa pelo Studio.
- Histórico: `select email, titulo, status, video_id, criado_em from youtube_envios order by criado_em desc;`
- Revogar: remover o app em myaccount.google.com/permissions da conta do canal (e conectar de novo se precisar).
