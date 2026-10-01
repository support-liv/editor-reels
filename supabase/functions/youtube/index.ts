// Edge Function "youtube": envia shorts pro YouTube sem a credencial sair do servidor.
// - Conectar canal (só administradores): troca o código do Google pelo refresh token e guarda no Vault.
// - Enviar: abre uma sessão de upload "resumable" válida só pra aquele vídeo; o editor manda o arquivo direto
//   pro YouTube por essa URL. Segredos: YOUTUBE_CLIENT_ID e YOUTUBE_CLIENT_SECRET (OAuth "App para computador").
import { createClient } from "npm:@supabase/supabase-js@2.58.0";

const ESCOPO = "https://www.googleapis.com/auth/youtube.upload";
const json = (corpo: unknown, status = 200) =>
  new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json" } });

function chaveServidor(): string {
  const legado = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (legado) return legado;
  const novas = Deno.env.get("SUPABASE_SECRET_KEYS");
  if (novas) return Object.values(JSON.parse(novas))[0] as string;
  throw new Error("sem chave de servidor");
}

async function tokenGoogle(params: Record<string, string>) {
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: Deno.env.get("YOUTUBE_CLIENT_ID")!, client_secret: Deno.env.get("YOUTUBE_CLIENT_SECRET")!, ...params,
    }),
  });
  return { ok: r.ok, dados: await r.json() };
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return json({ erro: "use POST" }, 405);
  if (!Deno.env.get("YOUTUBE_CLIENT_ID") || !Deno.env.get("YOUTUBE_CLIENT_SECRET"))
    return json({ erro: "YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET não cadastrados nos secrets" }, 503);
  const token = (req.headers.get("Authorization") ?? "").replace(/^Bearer\s+/i, "");
  const admin = createClient(Deno.env.get("SUPABASE_URL")!, chaveServidor(), { auth: { persistSession: false } });
  const { data: u, error: eu } = await admin.auth.getUser(token);
  if (eu || !u?.user?.email) return json({ erro: "sessão inválida: python3 editor/conta.py entrar" }, 401);
  const email = u.user.email.toLowerCase();
  const [{ data: dom }, { data: bloq }, { data: adm }, { data: lista }] = await Promise.all([
    admin.from("dominios_permitidos").select("dominio").eq("dominio", email.split("@")[1] ?? "").maybeSingle(),
    admin.from("acessos_bloqueados").select("email").eq("email", email).maybeSingle(),
    admin.from("administradores").select("email").eq("email", email).maybeSingle(),
    admin.from("usuarios_permitidos").select("email").eq("email", email).maybeSingle(),
  ]);
  if (!dom || bloq || !(lista || adm)) return json({ erro: "acesso não autorizado para este e-mail" }, 403);

  let p: any;
  try { p = await req.json(); } catch { return json({ erro: "corpo JSON inválido" }, 400); }
  const canal = String(p.canal ?? "").toLowerCase();

  if (p.acao === "canais") {
    const { data } = await admin.from("youtube_canais").select("canal, nome, conectado_em");
    return json({ canais: data ?? [] });
  }

  if (p.acao === "url_autorizacao" || p.acao === "conectar") {
    if (!adm) return json({ erro: "só administradores conectam canais" }, 403);
    if (!/^[a-z0-9_-]+$/.test(canal)) return json({ erro: "canal inválido (ex.: liv, imigrar)" }, 400);
    const redirect = String(p.redirect_uri ?? "");
    if (!/^http:\/\/127\.0\.0\.1:\d+\/?$/.test(redirect)) return json({ erro: "redirect_uri precisa ser http://127.0.0.1:PORTA" }, 400);
    if (p.acao === "url_autorizacao") {
      const q = new URLSearchParams({
        client_id: Deno.env.get("YOUTUBE_CLIENT_ID")!, redirect_uri: redirect, response_type: "code", scope: ESCOPO,
        access_type: "offline", prompt: "select_account consent", code_challenge: String(p.code_challenge), code_challenge_method: "S256",
        state: String(p.state ?? ""),
      });
      return json({ url: `https://accounts.google.com/o/oauth2/v2/auth?${q}` });
    }
    const t = await tokenGoogle({ code: String(p.code), code_verifier: String(p.code_verifier), redirect_uri: redirect,
                                  grant_type: "authorization_code" });
    if (!t.ok || !t.dados.refresh_token) return json({ erro: "o Google não devolveu autorização", detalhe: t.dados.error }, 400);
    const { error } = await admin.rpc("yt_salvar_token", { p_canal: canal, p_nome: String(p.nome ?? canal),
                                                           p_token: t.dados.refresh_token, p_email: email });
    if (error) return json({ erro: "não consegui guardar a autorização" }, 500);
    return json({ ok: true, canal });
  }

  if (p.acao === "iniciar_envio") {
    const titulo = String(p.titulo ?? "").trim();
    const descricao = String(p.descricao ?? "");
    const tags: string[] = Array.isArray(p.tags) ? p.tags.map(String) : [];
    if (!titulo || titulo.length > 100 || /[<>]/.test(titulo)) return json({ erro: "título vazio, com mais de 100 caracteres ou com < >" }, 400);
    if (descricao.length > 5000 || /[<>]/.test(descricao)) return json({ erro: "descrição com mais de 5.000 caracteres ou com < >" }, 400);
    if (tags.join(",").length > 500) return json({ erro: "tags passam de 500 caracteres" }, 400);
    let publicar_em: string | null = null;
    if (p.publicar_em) {
      const d = new Date(p.publicar_em);
      if (isNaN(d.getTime()) || d.getTime() < Date.now() + 15 * 60 * 1000) return json({ erro: "publicar_em precisa ser uma data futura (15 min+)" }, 400);
      publicar_em = d.toISOString();
    }
    const tamanho = Number(p.tamanho);
    if (!(tamanho > 0 && tamanho < 4e9)) return json({ erro: "tamanho do arquivo inválido" }, 400);

    const { data: refresh } = await admin.rpc("yt_ler_token", { p_canal: canal });
    if (!refresh) return json({ erro: `canal '${canal}' não conectado` }, 404);
    const t = await tokenGoogle({ refresh_token: refresh as string, grant_type: "refresh_token" });
    if (!t.ok) return json({ erro: "autorização do canal expirou: um administrador precisa conectar de novo" }, 401);

    const status: Record<string, unknown> = { privacyStatus: "private", selfDeclaredMadeForKids: false };
    if (publicar_em) status.publishAt = publicar_em;
    const meta = {
      snippet: { title: titulo, description: descricao, tags, categoryId: String(p.categoria ?? "27"),
                 defaultLanguage: "pt-BR", defaultAudioLanguage: "pt-BR" },
      status,
    };
    const r = await fetch("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", {
      method: "POST",
      headers: { Authorization: `Bearer ${t.dados.access_token}`, "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Length": String(tamanho), "X-Upload-Content-Type": "video/mp4" },
      body: JSON.stringify(meta),
    });
    const upload_url = r.headers.get("Location");
    if (!r.ok || !upload_url) return json({ erro: `YouTube recusou (${r.status})`, detalhe: (await r.text()).slice(0, 500) }, 502);
    const { data: env } = await admin.from("youtube_envios")
      .insert({ canal, user_id: u.user.id, email, titulo, publicar_em, status: "enviando" }).select("id").single();
    return json({ envio_id: env?.id, upload_url });
  }

  if (p.acao === "concluir") {
    await admin.from("youtube_envios").update({ video_id: String(p.video_id ?? ""), status: p.video_id ? "enviado" : "falhou",
                                                atualizado_em: new Date().toISOString() })
      .eq("id", Number(p.envio_id)).eq("user_id", u.user.id);
    return json({ ok: true });
  }

  return json({ erro: "ação desconhecida" }, 400);
});
