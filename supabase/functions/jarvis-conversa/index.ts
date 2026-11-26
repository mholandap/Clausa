// Jarvis do Clausa: o "cérebro" da conversa (Gemini, faixa grátis).
// Onde fica: Supabase → Edge Functions → função "jarvis-conversa".
// Precisa do segredo GEMINI_API_KEY (Edge Functions → Secrets). A chave nunca sai daqui.
// Só responde para quem está logado com o e-mail do dono (o mesmo do jarvis.sql).

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
// Tenta o primeiro modelo; se o Google tiver aposentado o nome, tenta o próximo.
const MODELOS = (Deno.env.get("GEMINI_MODELO") || "gemini-flash-latest,gemini-2.5-flash,gemini-2.0-flash")
  .split(",").map((m) => m.trim()).filter(Boolean);

const json = (obj: unknown, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { ...CORS, "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ erro: "use POST" }, 405);
  try {
    const chave = Deno.env.get("GEMINI_API_KEY");
    if (!chave) return json({ erro: "sem-chave" }, 500);

    // 1) Confere se quem chamou é o dono (com o próprio login dele, pelo banco)
    const url = Deno.env.get("SUPABASE_URL")!;
    const h = {
      apikey: req.headers.get("apikey") || Deno.env.get("SUPABASE_ANON_KEY") || "",
      Authorization: req.headers.get("Authorization") || "",
      "Content-Type": "application/json",
    };
    const r1 = await fetch(`${url}/rest/v1/rpc/jarvis_eh_dono`, { method: "POST", headers: h, body: "{}" });
    if (!r1.ok || (await r1.json()) !== true) {
      // Diz o motivo: sem login, ou logado com outro e-mail
      const u = await fetch(`${url}/auth/v1/user`, { headers: h });
      if (!u.ok) return json({ erro: "sem-login" }, 401);
      const email = (await u.json())?.email || "";
      return json({ erro: "outro-email", email }, 403);
    }

    // 2) Pega o último resumo do dia (o mesmo que a tela lê)
    const r2 = await fetch(`${url}/rest/v1/jarvis_resumos?select=conteudo,criado_em&order=criado_em.desc&limit=1`, { headers: h });
    const linhas = r2.ok ? await r2.json() : [];
    const resumo = linhas[0] ? JSON.stringify(linhas[0]) : "(nenhum resumo salvo ainda)";

    // 3) Pergunta e um pouco da conversa anterior
    const corpo = await req.json().catch(() => ({}));
    const pergunta = String(corpo.pergunta || "").slice(0, 600).trim();
    if (!pergunta) return json({ erro: "sem-pergunta" }, 400);
    const historico = (Array.isArray(corpo.historico) ? corpo.historico : []).slice(-8)
      .map((t: { papel?: string; texto?: string }) => ({
        role: t.papel === "jarvis" ? "model" : "user",
        parts: [{ text: String(t.texto || "").slice(0, 800) }],
      }));

    const agora = new Date().toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo", dateStyle: "full", timeStyle: "short" });
    const instrucoes = `Você é o Jarvis, assistente pessoal do Pedro, criador do Clausa (app que aponta cláusulas de atenção em contratos; hoje funciona por regras, sem IA). Ele mora em Brasília.
Agora é ${agora} (horário de Brasília).
Responda SEMPRE em português do Brasil, em tom elegante e prestativo, como um mordomo britânico bem-humorado. Às vezes chame-o de "senhor".
Sua resposta será FALADA em voz alta: de 1 a 4 frases curtas, sem listas, sem markdown, sem emojis, sem links.
Use o resumo do dia abaixo como fonte. Se a resposta não estiver no resumo e não for conhecimento geral, diga com franqueza que não sabe. Nunca invente números, nomes, curtidas, clientes ou compromissos.
Você não envia e-mails, não publica e não apaga nada; se ele pedir isso, diga que essa parte ele faz, ou o Claude com a aprovação dele.
Resumo do dia (JSON): ${resumo}`;

    const pedido = JSON.stringify({
      system_instruction: { parts: [{ text: instrucoes }] },
      contents: [...historico, { role: "user", parts: [{ text: pergunta }] }],
      generationConfig: { temperature: 0.7 },
    });

    for (const modelo of MODELOS) {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${modelo}:generateContent`, {
        method: "POST", headers: { "Content-Type": "application/json", "x-goog-api-key": chave }, body: pedido,
      });
      if (r.status === 404) continue; // nome de modelo que não existe mais
      if (r.status === 429) return json({ erro: "limite" }, 429);
      const d = await r.json();
      if (!r.ok) return json({ erro: "gemini", detalhe: d?.error?.message || r.status }, 502);
      const texto = (d?.candidates?.[0]?.content?.parts || []).map((p: { text?: string }) => p.text || "").join("").trim();
      return json({ resposta: texto || "Perdão, senhor, não consegui formular uma resposta.", modelo });
    }
    return json({ erro: "sem-modelo" }, 502);
  } catch (e) {
    return json({ erro: "falha", detalhe: String(e) }, 500);
  }
});
