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
// (Os Gemini 2.5 saíram do ar em nov/2026; a pesquisa usa as nossas ferramentas abaixo.)
const MODELOS = (Deno.env.get("GEMINI_MODELO") || "gemini-flash-lite-latest,gemini-flash-latest")
  .split(",").map((m) => m.trim()).filter(Boolean);

const VERSAO = 8;
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
    if (corpo.aquecer) return json({ ok: true }); // só acorda a função
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
REGRA DA PESQUISA: se a pergunta NÃO for sobre o dia dele (notícias, mundo, esportes, cotações, pessoas famosas, qualquer fato que possa ter mudado), você é OBRIGADO a usar uma ferramenta de pesquisa antes de responder (google_search, ou pesquisar_noticias e cotacao_moeda), mesmo que ache que já sabe. Responda com o que encontrou e diga a fonte em poucas palavras ("segundo o g1"). Não responda "não tenho registros": pesquise. Só diga que não sabe se a pesquisa não trouxer nada.
Você não envia e-mails, não publica e não apaga nada; se ele pedir isso, diga que essa parte ele faz, ou o Claude com a aprovação dele.
Resumo do dia dele (JSON; use só para perguntas sobre o dia dele): ${resumo}`;

    const base = {
      system_instruction: { parts: [{ text: instrucoes }] },
      contents: [...historico, { role: "user", parts: [{ text: pergunta }] }],
    };
    // "Pensar pouco": resposta falada e curta não precisa de raciocínio longo.
    const pensar = (m: string) => /2\.5/.test(m) ? { thinkingBudget: 0 } : { thinkingLevel: "minimal" };
    // Modos de pesquisa: "google" (busca do próprio Gemini, só nos 2.5 na faixa grátis),
    // "ferramentas" (nossas: Google Notícias e cotação, funcionam em qualquer modelo) ou "nenhum".
    type Modo = "google" | "ferramentas" | "nenhum";
    const ferramentas = [{ functionDeclarations: [
      { name: "pesquisar_noticias", description: "Pesquisa notícias recentes no Google Notícias (Brasil, em português). Use para qualquer fato atual: notícias, esportes, política, pessoas, eventos. Deixe a consulta vazia para as principais manchetes do dia.",
        parameters: { type: "OBJECT", properties: { consulta: { type: "STRING", description: "Palavras-chave curtas, ex.: 'resultado Flamengo', 'eleições EUA'. Vazio = principais manchetes." } } } },
      { name: "cotacao_moeda", description: "Cotação de referência do dia de uma moeda em reais (atualizada uma vez por dia).",
        parameters: { type: "OBJECT", properties: { moeda: { type: "STRING", description: "Código da moeda, ex.: USD, EUR, GBP, BTC não é suportado." } }, required: ["moeda"] } },
    ] }];
    const chamar = (modelo: string, comPensar: boolean, modo: Modo, conteudos: unknown[]) =>
      fetch(`https://generativelanguage.googleapis.com/v1beta/models/${modelo}:generateContent`, {
        method: "POST", headers: { "Content-Type": "application/json", "x-goog-api-key": chave },
        body: JSON.stringify({
          system_instruction: base.system_instruction, contents: conteudos,
          ...(modo === "google" ? { tools: [{ google_search: {} }] } : modo === "ferramentas" ? { tools: ferramentas } : {}),
          generationConfig: { temperature: 0.7, ...(comPensar ? { thinkingConfig: pensar(modelo) } : {}) },
        }),
        signal: AbortSignal.timeout(Math.max(1000, Math.min(10000, 28000 - (Date.now() - t0)))),
      });

    let limite = false, ultimoErro = "";
    const tentativas: string[] = [];
    for (const modelo of MODELOS) {
      if (Date.now() - t0 > 27000) break; // não passar de ~30 s no total
      const modos: Modo[] = podeBuscar(modelo) ? ["google", "ferramentas", "nenhum"] : ["ferramentas", "nenhum"];
      let r: Response | null = null, modo: Modo = modos[0], comPensar = true, conteudos: unknown[] = base.contents;
      try {
        for (modo of modos) {
          r = await chamar(modelo, comPensar, modo, conteudos);
          if (r.status === 400 && comPensar) { comPensar = false; r = await chamar(modelo, false, modo, conteudos); } // não aceita o ajuste de "pensar"
          tentativas.push(`${modelo}+${modo}:${r.status}`); passo(`${modelo} ${modo} ${r.status}`);
          if (r.status === 400 || (r.status === 429 && modo === "google")) continue; // esse modo não serve aqui: tenta o próximo
          break;
        }
      } catch (_) { ultimoErro = "demorou: " + modelo; tentativas.push(modelo + ":demorou"); passo(modelo + " demorou"); continue; }
      if (!r || r.status === 404) continue; // nome de modelo que não existe mais
      if (r.status === 429) { limite = true; continue; } // limite deste modelo: tenta outro
      let d = await r.json().catch(() => ({}));
      if (!r.ok) { ultimoErro = (d?.error?.message || String(r.status)).slice(0, 160); continue; }

      // Se o modelo pediu para usar nossas ferramentas, executa e devolve o resultado (até 3 rodadas)
      let fonte = d?.candidates?.[0]?.groundingMetadata?.webSearchQueries?.length ? "google" : "";
      try {
        for (let rodada = 0; rodada < 3; rodada++) {
          const partes = d?.candidates?.[0]?.content?.parts || [];
          const pedidos = partes.filter((p: { functionCall?: unknown }) => p.functionCall);
          if (!pedidos.length) break;
          const respostas = [];
          for (const p of pedidos) {
            const { name, args } = p.functionCall;
            const resultado = name === "cotacao_moeda" ? await cotacao(String(args?.moeda || "USD")) : await noticias(String(args?.consulta || ""));
            fonte = fonte || (name === "cotacao_moeda" ? "cotacao" : "noticias");
            passo(`${name}(${JSON.stringify(args || {})})`);
            respostas.push({ functionResponse: { name, response: { resultado } } });
          }
          conteudos = [...conteudos, { role: "model", parts: partes }, { role: "user", parts: respostas }];
          const r2 = await chamar(modelo, comPensar, modo, conteudos);
          tentativas.push(`${modelo}+resposta:${r2.status}`);
          if (!r2.ok) break;
          d = await r2.json();
        }
      } catch (e) { passo("ferramenta falhou " + String(e)); }

      const texto = (d?.candidates?.[0]?.content?.parts || []).map((p: { text?: string }) => p.text || "").join("")
        .replace(/\[\d+(,\s*\d+)*\]/g, "").replace(/[*_#`]/g, "").replace(/https?:\/\/\S+/g, "").replace(/\s+/g, " ").replace(/\s+([,.!?;:])/g, "$1").trim(); // vai ser falado
      if (!texto) { ultimoErro = "resposta vazia: " + modelo; continue; }
      return json({ resposta: texto, modelo, pesquisou: !!fonte, fonte, tentativas: tentativas.join(" ") });
    }
    if (limite) return json({ erro: "limite", detalhe: tentativas.join(" ") }, 429);
    return json({ erro: "sem-modelo", detalhe: tentativas.join(" ") + " | " + ultimoErro }, 502);
  } catch (e) {
    passo("falha " + String(e));
    return json({ erro: "falha", detalhe: String(e).slice(0, 200) }, 500);
  }
});

// ---------- ferramentas de pesquisa grátis ----------
const desfaz = (t: string) => t.replace(/<!\[CDATA\[|\]\]>/g, "").replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").trim();
async function noticias(consulta: string) {
  const q = consulta.trim();
  const url = q
    ? `https://news.google.com/rss/search?q=${encodeURIComponent(q + " when:7d")}&hl=pt-BR&gl=BR&ceid=BR:pt-419`
    : "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419";
  const r = await fetch(url, { signal: AbortSignal.timeout(4000) });
  if (!r.ok) return { erro: "Google Notícias respondeu " + r.status };
  const xml = await r.text();
  const itens = [...xml.matchAll(/<item>([\s\S]*?)<\/item>/g)].slice(0, 8).map((m) => {
    const pega = (tag: string) => desfaz((m[1].match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`)) || [])[1] || "");
    return { titulo: pega("title"), fonte: pega("source"), data: pega("pubDate") };
  });
  return itens.length ? { consulta: q || "principais manchetes", noticias: itens } : { consulta: q, noticias: [], aviso: "nada encontrado" };
}
async function cotacao(moeda: string) {
  const m = moeda.toUpperCase().replace(/[^A-Z]/g, "").slice(0, 3) || "USD";
  const r = await fetch(`https://open.er-api.com/v6/latest/${m}`, { signal: AbortSignal.timeout(6000) });
  const d = await r.json().catch(() => ({}));
  if (d?.result !== "success" || !d?.rates?.BRL) return { erro: "cotação indisponível para " + m };
  return { moeda: m, em_reais: Math.round(d.rates.BRL * 100) / 100, atualizado: d.time_last_update_utc, observacao: "cotação de referência, atualizada uma vez por dia" };
}
