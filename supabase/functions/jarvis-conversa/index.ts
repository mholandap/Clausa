// Jarvis do Clausa: o "cérebro" da conversa (Gemini, faixa grátis).
// Onde fica: Supabase → Edge Functions → função "jarvis-conversa".
// Precisa do segredo GEMINI_API_KEY (Edge Functions → Secrets). A chave nunca sai daqui.
// Só responde para quem está logado com o e-mail do dono (o mesmo do jarvis.sql).

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
// Tenta o primeiro modelo; se o nome não existir, demorar ou bater limite, tenta o próximo.
// Os 2.5 vêm primeiro porque, na faixa grátis, só eles podem pesquisar no Google (500 por dia, somando os dois).
const MODELOS = (Deno.env.get("GEMINI_MODELO") || "gemini-2.5-flash-lite,gemini-2.5-flash,gemini-flash-lite-latest,gemini-flash-latest")
  .split(",").map((m) => m.trim()).filter(Boolean);

const VERSAO = 6;
const podeBuscar = (m: string) => /2\.5-flash/.test(m);
const json = (obj: Record<string, unknown>, status = 200) =>
  new Response(JSON.stringify({ ...obj, versao: VERSAO }), { status, headers: { ...CORS, "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ erro: "use POST" }, 405);
  const t0 = Date.now(), passo = (p: string) => console.log(`[jarvis] ${p} (${Date.now() - t0} ms)`);
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

    passo("dono ok");
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
Sobre o dia dele (Clausa, Instagram, e-mails, agenda), use só o resumo abaixo; se não estiver lá, diga que não sabe. Nunca invente números, nomes, curtidas, clientes ou compromissos.
REGRA DA PESQUISA: se a pergunta NÃO for sobre o dia dele (por exemplo notícias, mundo, esportes, cotações, clima, pessoas famosas, qualquer fato que possa ter mudado), você é OBRIGADO a usar a ferramenta google_search antes de responder, mesmo que ache que já sabe. Responda com o que encontrou e diga a fonte em poucas palavras ("segundo o g1"). Não responda "não tenho registros": pesquise. Só diga que não sabe se a pesquisa não trouxer nada.
Você não envia e-mails, não publica e não apaga nada; se ele pedir isso, diga que essa parte ele faz, ou o Claude com a aprovação dele.
Resumo do dia dele (JSON; use só para perguntas sobre o dia dele): ${resumo}`;

    const base = {
      system_instruction: { parts: [{ text: instrucoes }] },
      contents: [...historico, { role: "user", parts: [{ text: pergunta }] }],
    };
    // "Pensar pouco": resposta falada e curta não precisa de raciocínio longo.
    const pensar = (m: string) => /2\.5/.test(m) ? { thinkingBudget: 0 } : { thinkingLevel: "minimal" };
    const chamar = (modelo: string, comPensar: boolean, comBusca: boolean) =>
      fetch(`https://generativelanguage.googleapis.com/v1beta/models/${modelo}:generateContent`, {
        method: "POST", headers: { "Content-Type": "application/json", "x-goog-api-key": chave },
        body: JSON.stringify({
          ...base,
          ...(comBusca ? { tools: [{ google_search: {} }] } : {}),
          generationConfig: { temperature: 0.7, ...(comPensar ? { thinkingConfig: pensar(modelo) } : {}) },
        }),
        signal: AbortSignal.timeout(Math.max(1000, Math.min(10000, 28000 - (Date.now() - t0)))),
      });

    let limite = false, ultimoErro = "";
    const tentativas: string[] = [];
    for (const modelo of MODELOS) {
      if (Date.now() - t0 > 27000) break; // não passar de ~30 s no total
      let r: Response, busca = podeBuscar(modelo);
      try {
        r = await chamar(modelo, true, busca);
        if (r.status === 400) r = await chamar(modelo, false, busca); // modelo que não aceita o ajuste de "pensar"
        if ((r.status === 400 || r.status === 429) && busca) { busca = false; r = await chamar(modelo, false, false); } // pesquisa indisponível ou cota da pesquisa acabou
      } catch (_) { ultimoErro = "demorou: " + modelo; tentativas.push(modelo + ":demorou"); passo(modelo + " demorou"); continue; }
      tentativas.push(modelo + (busca ? "+busca" : "") + ":" + r.status); passo(modelo + (busca ? " +busca " : " ") + r.status);
      if (r.status === 404) continue; // nome de modelo que não existe mais
      if (r.status === 429) { limite = true; continue; } // limite deste modelo: tenta outro
      const d = await r.json().catch(() => ({}));
      if (!r.ok) { ultimoErro = (d?.error?.message || String(r.status)).slice(0, 160); continue; }
      const texto = (d?.candidates?.[0]?.content?.parts || []).map((p: { text?: string }) => p.text || "").join("")
        .replace(/\[\d+(,\s*\d+)*\]/g, "").replace(/[*_#`]/g, "").replace(/https?:\/\/\S+/g, "").replace(/\s+/g, " ").replace(/\s+([,.!?;:])/g, "$1").trim(); // vai ser falado
      const pesquisou = !!d?.candidates?.[0]?.groundingMetadata?.webSearchQueries?.length;
      return json({ resposta: texto || "Perdão, senhor, não consegui formular uma resposta.", modelo, pesquisou });
    }
    if (limite) return json({ erro: "limite", detalhe: tentativas.join(" ") }, 429);
    return json({ erro: "sem-modelo", detalhe: tentativas.join(" ") + " | " + ultimoErro }, 502);
  } catch (e) {
    passo("falha " + String(e));
    return json({ erro: "falha", detalhe: String(e).slice(0, 200) }, 500);
  }
});
