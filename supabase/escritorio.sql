-- Clausa: conta de equipe (escritório).
-- Como usar: Supabase → SQL Editor → New query → cole TUDO → Run. Pode rodar de novo sem problema.
-- O que cria: escritório, membros (admin/membro), convite por código e regras compartilhadas.
-- Os CONTRATOS continuam individuais: ninguém da equipe vê o contrato do colega.

create table if not exists public.escritorios (
  id          uuid primary key default gen_random_uuid(),
  nome        text not null check (length(nome) between 2 and 80),
  convite     text not null unique default replace(gen_random_uuid()::text, '-', ''),
  criado_por  uuid not null default auth.uid(),
  criado_em   timestamptz not null default now()
);

create table if not exists public.membros (
  escritorio_id uuid not null references public.escritorios(id) on delete cascade,
  user_id       uuid not null unique,                 -- cada pessoa em um escritório só
  email         text,
  papel         text not null default 'membro' check (papel in ('admin','membro')),
  entrou_em     timestamptz not null default now(),
  primary key (escritorio_id, user_id)
);

create table if not exists public.escritorio_regras (
  escritorio_id  uuid primary key references public.escritorios(id) on delete cascade,
  regras         jsonb not null,
  atualizado_em  timestamptz not null default now(),
  atualizado_por text
);

alter table public.escritorios       enable row level security;
alter table public.membros           enable row level security;
alter table public.escritorio_regras enable row level security;

-- Funções de apoio (evitam regra de acesso circular)
create or replace function public.meu_escritorio() returns uuid
language sql stable security definer set search_path = public as $$
  select escritorio_id from membros where user_id = auth.uid()
$$;
create or replace function public.sou_admin(esc uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists(select 1 from membros where escritorio_id = esc and user_id = auth.uid() and papel = 'admin')
$$;

-- Quem é da equipe vê o próprio escritório, os colegas e as regras
drop policy if exists "esc: membro ve"   on public.escritorios;
drop policy if exists "esc: admin muda"  on public.escritorios;
drop policy if exists "esc: admin apaga" on public.escritorios;
drop policy if exists "mem: equipe ve"   on public.membros;
drop policy if exists "mem: admin tira"  on public.membros;
drop policy if exists "reg: equipe ve"   on public.escritorio_regras;
drop policy if exists "reg: admin grava" on public.escritorio_regras;
drop policy if exists "reg: admin muda"  on public.escritorio_regras;

create policy "esc: membro ve"   on public.escritorios for select to authenticated using (id = public.meu_escritorio());
create policy "esc: admin muda"  on public.escritorios for update to authenticated using (public.sou_admin(id)) with check (public.sou_admin(id));
create policy "esc: admin apaga" on public.escritorios for delete to authenticated using (public.sou_admin(id));
create policy "mem: equipe ve"   on public.membros for select to authenticated using (escritorio_id = public.meu_escritorio());
-- o admin tira alguém; qualquer pessoa pode sair (apagar a própria linha)
create policy "mem: admin tira"  on public.membros for delete to authenticated using (public.sou_admin(escritorio_id) or user_id = auth.uid());
create policy "reg: equipe ve"   on public.escritorio_regras for select to authenticated using (escritorio_id = public.meu_escritorio());
create policy "reg: admin grava" on public.escritorio_regras for insert to authenticated with check (public.sou_admin(escritorio_id));
create policy "reg: admin muda"  on public.escritorio_regras for update to authenticated using (public.sou_admin(escritorio_id)) with check (public.sou_admin(escritorio_id));

grant select, update, delete on public.escritorios to authenticated;
grant select, delete on public.membros to authenticated;
grant select, insert, update on public.escritorio_regras to authenticated;

-- Criar escritório: quem cria vira admin
create or replace function public.criar_escritorio(p_nome text) returns public.escritorios
language plpgsql security definer set search_path = public as $$
declare e escritorios;
begin
  if auth.uid() is null then raise exception 'entre na sua conta' using errcode = '42501'; end if;
  if exists(select 1 from membros where user_id = auth.uid()) then raise exception 'voce ja faz parte de um escritorio'; end if;
  insert into escritorios (nome, criado_por) values (trim(p_nome), auth.uid()) returning * into e;
  insert into membros (escritorio_id, user_id, email, papel) values (e.id, auth.uid(), auth.jwt() ->> 'email', 'admin');
  return e;
end $$;

-- Entrar com o código do convite
create or replace function public.entrar_escritorio(p_convite text) returns public.escritorios
language plpgsql security definer set search_path = public as $$
declare e escritorios;
begin
  if auth.uid() is null then raise exception 'entre na sua conta' using errcode = '42501'; end if;
  select * into e from escritorios where convite = trim(p_convite);
  if e.id is null then raise exception 'convite invalido'; end if;
  if exists(select 1 from membros where user_id = auth.uid() and escritorio_id <> e.id) then raise exception 'voce ja faz parte de outro escritorio'; end if;
  insert into membros (escritorio_id, user_id, email, papel) values (e.id, auth.uid(), auth.jwt() ->> 'email', 'membro')
    on conflict (escritorio_id, user_id) do nothing;
  return e;
end $$;

-- Trocar o código do convite (o link antigo deixa de funcionar)
create or replace function public.novo_convite(p_esc uuid) returns text
language plpgsql security definer set search_path = public as $$
declare c text := replace(gen_random_uuid()::text, '-', '');
begin
  if not public.sou_admin(p_esc) then raise exception 'so o administrador' using errcode = '42501'; end if;
  update escritorios set convite = c where id = p_esc;
  return c;
end $$;

revoke all on function public.criar_escritorio(text) from public;
revoke all on function public.entrar_escritorio(text) from public;
revoke all on function public.novo_convite(uuid) from public;
grant execute on function public.criar_escritorio(text), public.entrar_escritorio(text), public.novo_convite(uuid),
  public.meu_escritorio(), public.sou_admin(uuid) to authenticated;

select 'Pronto: conta de equipe criada.' as resultado;
