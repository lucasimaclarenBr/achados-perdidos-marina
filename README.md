# ⚓ Achados & Perdidos — Marina Barra Clube

Sistema de gestão de achados e perdidos desenvolvido para o Marina Barra Clube (Rio de Janeiro). Substitui um processo manual baseado em planilhas por uma solução centralizada, rastreável e acessível via navegador.

## 🌐 Acesso

**[aepmarina.streamlit.app](https://aepmarina.streamlit.app)**

---

## 🎯 Problema resolvido

O processo anterior dependia de planilhas isoladas e anotações manuais, gerando:
- Dificuldade de cruzar informações entre funcionários
- Risco de extravio de itens de valor
- Falta de rastreabilidade e prestação de contas

---

## ✅ Funcionalidades

### 📦 Cadastro de Itens
- Código único por categoria com controle de vagas disponíveis
- 12 categorias com capacidades físicas reais (ex: Roupas/300, Acessórios/100)
- Upload de foto vinculado ao item
- Identificação opcional do sócio com validação de telefone e número de título
- Flag independente de Caixa Azul (item separado para retirada rápida)

### 🔎 Busca Ativa (Tickets)
- Abertura de ticket quando sócio relata perda
- SLA automático de 10 dias para retorno
- Registro de categoria e descrição do item perdido

### 🗂️ Inventário e Pesquisa
- Tabela com filtros por categoria, status, caixa azul, texto livre e intervalo de datas
- Contagem de dias no status atual (calculada via histórico de movimentações)
- Busca sem distinção de acentos (BONE encontra BONÉ)
- Seleção múltipla via checkbox

### ✏️ Edição e Movimentação
- Edição de itens com campos em maiúsculo automático
- Histórico completo de edições por item
- Movimentação individual ou em lote com confirmação por senha
- Ciclo de vida controlado: Armazenado → Museu → A Doar/Descartados/Devolvidos

### 📤 Exportação
- Excel com cabeçalho estilizado e linhas alternadas
- PDF com rodapé institucional
- Exportar tudo (filtrado) ou somente itens selecionados

### 👥 Controle de Acesso
- Perfis: Consulta / Edição / Admin
- Login com senha por usuário
- Confirmação de senha para alterações críticas

---

## 🛠️ Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend / App | Python + Streamlit |
| Banco de dados | Supabase (PostgreSQL) |
| Storage de imagens | Supabase Storage |
| Deploy | Streamlit Community Cloud |
| Controle de versão | GitHub |

### Dependências principais
```
streamlit
supabase
pandas
fpdf2
openpyxl
pillow
unidecode
```

---

## 📁 Estrutura do projeto

```
achados-perdidos-marina/
├── .streamlit/
│   └── config.toml          # Tema dark, cor primária #00897b
├── assets/
│   └── logo_marina.png
├── infra/
│   ├── banco_dados.py       # Conexão Supabase
│   └── utils.py             # Funções de fuso horário (BRT)
├── telas/
│   ├── tela_cadastro.py     # Cadastro de itens e busca ativa
│   └── tela_busca.py        # Inventário, pesquisa e edição
├── app.py                   # Entry point, CSS global, roteamento
├── requirements.txt
└── CONTEXT.md               # Contexto do projeto para Claude Code
```

---

## 🗃️ Schema do banco

### Tabelas principais
- **`itens`** — inventário de objetos encontrados
- **`busca_ativa`** — tickets de sócios procurando itens perdidos
- **`historico_edicoes`** — log de todas as alterações realizadas
- **`usuarios`** — controle de acesso por perfil

### Ciclo de vida dos itens
```
Cadastro → Armazenado (60 dias)
               ↓
           Museu (30 dias)
               ↓
           A Doar → Doados
           Descartados
               ↓ (qualquer fase)
           Devolvidos
```

---

## 🚀 Rodando localmente

```bash
# Clone o repositório
git clone https://github.com/lucasimaclaren/achados-perdidos-marina.git
cd achados-perdidos-marina

# Crie o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Configure as credenciais do Supabase
# Crie o arquivo .streamlit/secrets.toml com:
# [supabase]
# url = "sua_url"
# key = "sua_key"

# Rode o app
streamlit run app.py
```

---

## 👨‍💻 Desenvolvimento

Projeto desenvolvido com assistência de IA (Claude — Anthropic) como portfólio técnico e solução pro bono para o Marina Barra Clube.

**Branch de trabalho:** `dev` → merge para `main` a cada funcionalidade concluída.
