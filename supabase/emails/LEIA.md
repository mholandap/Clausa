# E-mails do Clausa (modelos para o Supabase)

Onde colar: Supabase → Authentication → Emails → Templates. Em cada modelo, troque o **Assunto** e cole o HTML do arquivo no **corpo** (aba "Source"/"HTML"), depois clique em **Save**.

| Modelo no Supabase | Assunto | Arquivo |
|---|---|---|
| Confirm signup | Confirme seu e-mail para ativar o Clausa | `1-confirmar-cadastro.html` |
| Reset Password | Clausa: crie uma senha nova | `2-redefinir-senha.html` |
| Change Email Address | Clausa: confirme o seu novo e-mail | `3-trocar-email.html` |

Também em Authentication → URL Configuration:
- **Site URL:** `https://mholandap.github.io/Clausa/`
- **Redirect URLs:** adicionar `https://mholandap.github.io/Clausa/**`

(Quando houver domínio próprio, trocar os dois endereços e o logo.)
