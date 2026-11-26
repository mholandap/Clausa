-- Jarvis do Clausa: lugar protegido para guardar o resumo do dia.
-- Como usar: Supabase → SQL Editor → New query → cole TUDO → troque o e-mail na linha marcada → Run.
-- No fim aparece o "token do Jarvis": copie (é usado só para o Jarvis das 7h50 salvar o resumo).
-- Pode rodar de novo sem problema: não apaga nada e não troca o token.

-- 1) Tabela dos resumos (cada linha = um resumo do dia, em JSON)
create table if not exists public.jarvis_resumos (
  id         bigint generated always as identity primary key,
  criado_em  timestamptz not null default now(),
  dia        date not null default ((now() at time zone 'America/Sao_Paulo')::date),
  conteudo   jsonb not null
);
alter table public.jarvis_resumos enable row level security;

-- 2) Configuração privada (sem política nenhuma: ninguém lê pela internet)
create table if not exists public.jarvis_config (
  chave text primary key,
  valor text not null
);
alter table public.jarvis_config enable row level security;

insert into public.jarvis_config (chave, valor)
values ('dono_email', 'TROQUE_PELO_SEU_EMAIL_DE_LOGIN_NO_CLAUSA')   -- <<< TROQUE AQUI (entre as aspas simples)
on conflict (chave) do update set valor = excluded.valor;

insert into public.jarvis_config (chave, valor)
values ('token', replace(gen_random_uuid()::text || gen_random_uuid()::text, '-', ''))
on conflict (chave) do nothing;

-- 3) Só o dono (logado com o e-mail acima) lê os resumos
create or replace function public.jarvis_eh_dono() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce(lower(auth.jwt() ->> 'email') = lower((select valor from jarvis_config where chave = 'dono_email')), false)
$$;

drop policy if exists "jarvis: dono le" on public.jarvis_resumos;
create policy "jarvis: dono le" on public.jarvis_resumos
  for select to authenticated using (public.jarvis_eh_dono());
grant select on public.jarvis_resumos to authenticated;

-- 4) Porta de entrada para o Jarvis das 7h50 salvar o resumo.
--    Só aceita quem manda o cabeçalho x-jarvis-token com o token certo. Guarda 30 dias.
create or replace function public.jarvis_salvar(conteudo jsonb) returns bigint
language plpgsql security definer set search_path = public as $$
declare
  recebido text := current_setting('request.headers', true)::json ->> 'x-jarvis-token';
  novo bigint;
begin
  if recebido is null or recebido <> (select valor from jarvis_config where chave = 'token') then
    raise exception 'nao autorizado' using errcode = '42501';
  end if;
  insert into jarvis_resumos (conteudo) values (conteudo) returning id into novo;
  delete from jarvis_resumos where criado_em < now() - interval '30 days';
  return novo;
end $$;
revoke all on function public.jarvis_salvar(jsonb) from public;
grant execute on function public.jarvis_salvar(jsonb) to anon, authenticated;

-- 5) Mostra o token para você copiar
select valor as "token do Jarvis (copie)" from public.jarvis_config where chave = 'token';
