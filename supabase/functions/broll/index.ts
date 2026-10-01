// Edge Function "broll": busca vídeos de B-roll para o editor-reels sem expor a chave da API.
// O editor manda só a palavra de busca, com o login da pessoa (JWT do Supabase Auth). A chave do banco de
// imagens fica nos secrets do projeto (PEXELS_API_KEY), nunca no computador de quem usa.
import { createClient } from "npm:@supabase/supabase-js@2.58.0";

const LIMITE_DIA = 300;          // buscas por pessoa a cada 24h
const MAX_RESULTADOS = 15;

const json = (corpo: unknown, status = 200) =>
  new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json" } });

function chaveServidor(): string {
  const legado = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (legado) return legado;
  const novas = Deno.env.get("SUPABASE_SECRET_KEYS");     // {"default": "sb_secret_..."}
  if (novas) return Object.values(JSON.parse(novas))[0] as string;
  throw new Error("sem chave de servidor");
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return json({ erro: "use POST" }, 405);
  const url = Deno.env.get("SUPABASE_URL")!;
  const token = (req.headers.get("Authorization") ?? "").replace(/^Bearer\s+/i, "");
  if (!token) return json({ erro: "faça login: python3 editor/conta.py entrar" }, 401);

  // quem está pedindo (o JWT já passou pela verificação da plataforma; aqui pegamos o usuário atual)
  const admin = createClient(url, chaveServidor(), { auth: { persistSession: false } });
  const { data: u, error: eu } = await admin.auth.getUser(token);
  if (eu || !u?.user?.email) return json({ erro: "sessão inválida: entre de novo" }, 401);
  const email = u.user.email.toLowerCase();
  const dominio = email.split("@")[1] ?? "";

  const [{ data: dom }, { data: bloq }] = await Promise.all([
    admin.from("dominios_permitidos").select("dominio").eq("dominio", dominio).maybeSingle(),
    admin.from("acessos_bloqueados").select("email").eq("email", email).maybeSingle(),
  ]);
  if (!dom || bloq) return json({ erro: "acesso não autorizado para este e-mail" }, 403);

  const desde = new Date(Date.now() - 24 * 3600 * 1000).toISOString();
  const { count } = await admin.from("uso_api").select("id", { count: "exact", head: true })
    .eq("user_id", u.user.id).gte("criado_em", desde);
  if ((count ?? 0) >= LIMITE_DIA) return json({ erro: `limite de ${LIMITE_DIA} buscas por dia` }, 429);

  let pedido: { busca?: string; orientacao?: string; quantidade?: number; servico?: string };
  try { pedido = await req.json(); } catch { return json({ erro: "corpo JSON inválido" }, 400); }
  const busca = (pedido.busca ?? "").trim().slice(0, 100);
  if (!busca) return json({ erro: "informe 'busca'" }, 400);
  const orientacao = ["portrait", "landscape", "square"].includes(pedido.orientacao ?? "") ? pedido.orientacao! : "portrait";
  const quantidade = Math.min(Math.max(1, Number(pedido.quantidade) || 8), MAX_RESULTADOS);
  if ((pedido.servico ?? "pexels") !== "pexels") return json({ erro: "serviço não disponível" }, 400);

  const chave = Deno.env.get("PEXELS_API_KEY");
  if (!chave) return json({ erro: "PEXELS_API_KEY não cadastrada nos secrets do projeto" }, 503);
  const q = new URLSearchParams({ query: busca, orientation: orientacao, per_page: String(quantidade), size: "medium" });
  const r = await fetch(`https://api.pexels.com/videos/search?${q}`, { headers: { Authorization: chave } });
  if (!r.ok) return json({ erro: `pexels respondeu ${r.status}` }, 502);
  const dados = await r.json();

  // só o que o editor precisa: arquivos por qualidade + crédito do autor (o Pexels pede atribuição quando possível)
  const videos = (dados.videos ?? []).map((v: any) => ({
    id: v.id, largura: v.width, altura: v.height, duracao: v.duration, pagina: v.url, capa: v.image,
    autor: v.user?.name, autor_url: v.user?.url, fonte: "Pexels",
    arquivos: (v.video_files ?? []).filter((f: any) => f.file_type === "video/mp4")
      .map((f: any) => ({ qualidade: f.quality, largura: f.width, altura: f.height, fps: f.fps, link: f.link })),
  }));

  await admin.from("uso_api").insert({ user_id: u.user.id, email, servico: "pexels", consulta: busca, resultados: videos.length });
  return json({ busca, orientacao, videos });
});
