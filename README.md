# Ginseng Manutenção — v1

Sistema de gestão de manutenção (Lojas, Ordens de Serviço, Custos, Documentos e Dashboard),
recriado em Python (Flask) a partir da estrutura que você montou no Base44.

## O que já funciona nessa v1

- Login com 2 níveis: **Admin** (cria/edita/exclui tudo) e **Usuário** (só visualiza)
- **Dashboard** com KPIs de OS e custos
- **Lojas** — cadastro completo
- **Ordens de Serviço** — criação e mudança de status
- **Custos** — registro e listagem
- **Documentos** — pastas por loja, pastas personalizadas, upload de arquivos

**Fora da v1** (dá pra adicionar depois sem refazer nada): Chamados (Requests), Preventiva,
Equipamentos, Fornecedores (tela própria — hoje só existe internamente), Obras, Histórico,
Apresentações e o assistente de IA.

---

## PARTE 1 — Rodando no seu PC (primeiro teste)

### 1. Instalar o Python
- Baixe em: https://www.python.org/downloads/
- No instalador do Windows, **marque a caixinha "Add Python to PATH"** antes de clicar em instalar.
- Pra confirmar que funcionou, abra o Prompt de Comando (cmd) e digite: `python --version`

### 2. Abrir a pasta do projeto
- Extraia a pasta `ginseng_app` em algum lugar do seu PC (ex: Documentos).
- Abra o Prompt de Comando dentro dessa pasta (ou `cd caminho\da\pasta`).

### 3. Criar o "ambiente virtual" (isolamento das bibliotecas do projeto)
```
python -m venv venv
```

### 4. Ativar o ambiente virtual
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

Você vai ver `(venv)` aparecer no início da linha do terminal — é assim que sabe que funcionou.

### 5. Instalar as dependências
```
pip install -r requirements.txt
```

### 6. Rodar o site
```
python app.py
```

Vai aparecer algo como `Running on http://127.0.0.1:5000`. Abra esse endereço no navegador.

**Primeiro login:**
- E-mail: `admin@ginseng.com`
- Senha: `admin123`

**Troque essa senha antes de usar de verdade** (por enquanto, pra trocar, me avise que eu adiciono
uma tela de "editar meu perfil" — ainda não está na v1).

---

## PARTE 2 — Colocando no ar (hospedagem)

### Passo 1 — Criar o banco de dados definitivo (Supabase)

Por padrão, o projeto usa um arquivo local (SQLite) — bom só pra teste. Pra colocar no ar
de verdade, você precisa de um banco "de verdade":

1. Crie conta grátis em https://supabase.com
2. Crie um novo projeto (escolha uma senha forte pro banco e guarde ela)
3. No painel, vá em **Project Settings → Database → Connection String** e copie a URI
   (algo como `postgresql://postgres:[SUA-SENHA]@...supabase.co:5432/postgres`)
4. Ainda no Supabase, vá em **Storage** e crie um bucket chamado `documentos`, marcado como público

### Passo 2 — Subir o código pro GitHub

1. Crie conta em https://github.com (se ainda não tiver)
2. Crie um novo repositório (pode ser privado)
3. Dentro da pasta do projeto no seu PC:
```
git init
git add .
git commit -m "Primeira versão"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/NOME-DO-REPO.git
git push -u origin main
```

### Passo 3 — Hospedar no Render

1. Crie conta grátis em https://render.com (dá pra entrar direto com GitHub)
2. Clique em **New → Web Service**
3. Conecte o repositório que você acabou de criar
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:create_app()`
5. Em **Environment Variables**, adicione:
   - `SECRET_KEY` → qualquer texto longo e aleatório
   - `DATABASE_URL` → a URI do Supabase que você copiou no Passo 1
   - `STORAGE_BACKEND` → `supabase`
   - `SUPABASE_URL` → URL do projeto Supabase (Project Settings → API)
   - `SUPABASE_KEY` → a chave `service_role` (Project Settings → API)
   - `SUPABASE_BUCKET` → `documentos`
6. Clique em **Create Web Service**

O Render vai te dar um link tipo `ginseng-manutencao.onrender.com` — é o site no ar, de verdade,
acessível de qualquer lugar.

---

## Dúvidas comuns

**"Deu erro ao instalar as dependências"** — geralmente falta o Python atualizado. Confirma a
versão com `python --version` (precisa ser 3.10 ou mais novo).

**"O site local não abre"** — confirma que o `(venv)` está ativo no terminal antes de rodar
`python app.py`.

**"Esqueci a senha do admin"** — por enquanto, apague o arquivo `app.db` e rode de novo; ele
recria o admin padrão (mas também apaga todos os dados — cuidado).

Se travar em qualquer passo, me manda a mensagem de erro exata que eu te ajudo a resolver.
