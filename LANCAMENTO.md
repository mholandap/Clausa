# Clausa: o que falta para lançar

Atualizado em 27/11/2026. ✅ = pronto · ⏳ = depende do Pedro · 🔧 = Claude faz depois que o Pedro concluir o passo anterior.

## Já pronto no app
- ✅ Leitura de contratos por regras (PDF, Word, .txt, texto colado e **PDF escaneado**, lido no próprio aparelho)
- ✅ Contratos longos: todos os trechos, com "Cláusula X · item Y"
- ✅ Relatório em **PDF** e em **Word**
- ✅ **Modo sigilo** (o contrato não vai para a nuvem)
- ✅ **Conta de equipe**: escritório, convite por link e regras compartilhadas (falta ativar: passo 1)
- ✅ App instalável no celular, com aviso de versão nova
- ✅ Proposta de piloto para escritórios (`marketing/proposta/`)

## Passos do Pedro (em ordem)

### 1. Ativar a conta de equipe (2 minutos) ⏳
Supabase → SQL Editor → New query → cole todo o `supabase/escritorio.sql` → Run.
Aparece "Pronto: conta de equipe criada." Depois, no app: barra lateral → **Escritório**.

### 2. Domínio próprio (cerca de R$ 40 por ano) ⏳
- Em **registro.br**, procure um nome. `clausa.com.br` parece já ter dono; `useclausa.com.br` e `clausaapp.com.br` pareciam livres em 27/11, mas confirme lá.
- Compre com o seu CPF (ou com o CNPJ, quando tiver).
- 🔧 Depois, o Claude passa os registros de DNS, configura o GitHub Pages com HTTPS e atualiza o Supabase e os links.

### 3. E-mails de cadastro e "esqueci a senha" (grátis) ⏳ depois do passo 2
O envio padrão do Supabase **só entrega para a equipe do projeto** (2 por hora): clientes não recebem. Enquanto isso, "Confirm email" fica **desligado** (as pessoas entram direto) e o login com Google é o caminho recomendado. Os modelos de e-mail prontos estão em `supabase/emails/`. Para o lançamento, use um serviço próprio:
- Crie uma conta grátis no **Resend** (resend.com) e adicione o domínio do passo 2.
- 🔧 O Claude passa os registros de DNS. A chave do Resend vai **direto** no Supabase (Authentication → Emails → SMTP Settings), **nunca no chat**.
- Enquanto isso, o login com Google continua funcionando normalmente.

### 4. CNPJ ⏳
- Escritório pede **nota fiscal**. Veja no **Portal do Empreendedor (gov.br)** se a atividade de software entra no **MEI** (cerca de R$ 80 por mês de imposto fixo).
- Se não entrar, o caminho é uma **ME no Simples Nacional**, com contador.
- Na dúvida, uma conversa rápida com um contador resolve.

### 5. Preço ✅ (proposta do Pedro em 27/11; validar no piloto)
- **Grátis:** R$ 0. Análise e relatório em PDF, até 5 contratos salvos.
- **Profissional (autônomo):** **R$ 49/mês** (ou R$ 490/ano). Contratos ilimitados, Word, PDF escaneado, modo sigilo, regras próprias.
- **Escritório:** **R$ 39 por advogado/mês** (mínimo de 3). Tudo do Profissional, mais conta de equipe, regras do escritório e suporte direto.
- **Fundador:** quem fizer o piloto ganha 50% de desconto no primeiro ano.
- Na demonstração, perguntar à chefe quanto faria sentido pagar antes de dizer os valores.

### 6. Receber pagamento ⏳ depois dos passos 4 e 5
- Crie conta no **Asaas** ou no **Mercado Pago** (ambos aceitam Pix, boleto e cartão; cobram taxa por venda, sem mensalidade).
- 🔧 O Claude constrói a assinatura no app (liberar o acesso de quem pagou). A chave da conta de pagamento vai **direto** no Supabase, nunca no chat.

### 7. Termos e privacidade revisados ⏳
- `termos.html` e `privacidade.html` já descrevem o app de hoje (sigilo, equipe, leitura no aparelho).
- Peça para uma advogada revisar, como a do piloto, em troca do acesso. Depois da revisão, o Claude aplica as mudanças.

## Depois do lançamento (não bloqueia)
- Prazos e due diligence (estão como "em breve" no site)
- Versão com IA (quando houver dinheiro)
- Play Store
