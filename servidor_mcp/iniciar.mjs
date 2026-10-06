#!/usr/bin/env node
// Inicia o servidor MCP do Editor Reels no Mac ou no Windows.
// O plugin instalado não traz os arquivos grandes (Git LFS), então o servidor roda a partir da PASTA DE TRABALHO
// completa (clone do repositório com estoque, trilhas e transições). Ordem de busca:
//   1) variável EDITOR_REELS_DIR   2) Mesa/editor-reels   3) pasta do usuário/editor-reels
// Se a pasta existe, atualiza em silêncio (git pull + lfs pull, com limite de tempo) e sobe o servidor Python.
// Se não existe, sobe um servidor mínimo que só explica como instalar (a skill editor-de-videos faz isso).
import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { homedir, platform } from "node:os";
import { join } from "node:path";

const WIN = platform() === "win32";
const casa = homedir();

function mesa() {
  if (WIN) {
    const r = spawnSync("powershell", ["-NoProfile", "-Command", "[Environment]::GetFolderPath('Desktop')"], { encoding: "utf8" });
    const p = (r.stdout || "").trim();
    if (p && existsSync(p)) return p;
  }
  return join(casa, "Desktop");
}

const candidatos = [process.env.EDITOR_REELS_DIR, join(mesa(), "editor-reels"), join(casa, "editor-reels")].filter(Boolean);
const pasta = candidatos.find((p) => existsSync(join(p, "servidor_mcp", "servidor.py")));

function python() {
  if (!WIN) return ["python3", []];
  const r = spawnSync("py", ["-3.12", "--version"], { encoding: "utf8" });
  return r.status === 0 ? ["py", ["-3.12", "-X", "utf8"]] : ["python", ["-X", "utf8"]];
}

if (!pasta) {
  // ainda não instalado: servidor mínimo em Node que responde só a ferramenta "situacao"
  const passos = "O editor ainda não está instalado neste computador. Clone https://github.com/support-liv/editor-reels.git " +
    "na Mesa (pasta editor-reels), rode o instalador (Windows: setup.ps1; Mac: setup.sh), depois reinicie o Claude.";
  process.stdin.setEncoding("utf8");
  let buf = "";
  const enviar = (o) => process.stdout.write(JSON.stringify(o) + "\n");
  process.stdin.on("data", (d) => {
    buf += d;
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const linha = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
      if (!linha) continue;
      const m = JSON.parse(linha);
      if (m.method === "initialize")
        enviar({ jsonrpc: "2.0", id: m.id, result: { protocolVersion: m.params.protocolVersion, capabilities: { tools: {} },
          serverInfo: { name: "editor-reels", version: "instalacao" }, instructions: passos } });
      else if (m.method === "tools/list")
        enviar({ jsonrpc: "2.0", id: m.id, result: { tools: [{ name: "situacao", description: "Diz se o editor está instalado e como instalar.",
          inputSchema: { type: "object", properties: {} } }] } });
      else if (m.method === "tools/call")
        enviar({ jsonrpc: "2.0", id: m.id, result: { content: [{ type: "text", text: passos }] } });
      else if (m.id !== undefined) enviar({ jsonrpc: "2.0", id: m.id, result: {} });
    }
  });
} else {
  // atualiza em silêncio (sem travar o início se estiver sem internet)
  spawnSync("git", ["-C", pasta, "pull", "--ff-only", "-q"], { timeout: 20000, stdio: "ignore" });
  spawnSync("git", ["-C", pasta, "lfs", "pull"], { timeout: 60000, stdio: "ignore" });
  const [cmd, pre] = python();
  const p = spawn(cmd, [...pre, join(pasta, "servidor_mcp", "servidor.py")], {
    stdio: "inherit", env: { ...process.env, PYTHONUTF8: "1", EDITOR_REELS_DIR: pasta },
  });
  p.on("exit", (c) => process.exit(c ?? 0));
}
