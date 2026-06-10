# Contexto do Projeto — Achados e Perdidos Marina Barra Clube

## Visão Geral
Sistema de gestão de achados e perdidos para o Marina Barra Clube (Rio de Janeiro), desenvolvido pro bono. Stack: Python + Streamlit + Supabase.

## Estrutura do Projeto
```
achados-perdidos-marina/
├── .streamlit/
│   └── config.toml          # Tema dark, cor primária #00897b
├── assets/
│   └── logo_marina.png
├── infra/
│   └── banco_dados.py       # Conexão Supabase
├── telas/
│   ├── tela_cadastro.py     # Fase 1 — CONCLUÍDA
│   └── tela_busca.py        # Fase 2 — CONCLUÍDA
├── app.py                   # Entry point, CSS global, roteamento, login
├── requirements.txt
└── CONTEXT.md
```

## Stack e Dependências
- **Frontend/App:** Streamlit
- **Banco de dados:** Supabase (PostgreSQL)
- **Dependências:** streamlit, pandas, supabase, pillow, unidecode, fpdf2, openpyxl

## Schema do Banco (Supabase)

### Tabela `itens`
| Coluna | Tipo | Obs |
|--------|------|-----|
| codigo_item | VARCHAR(20) PK | Formato: 001AC, 042R, etc. |
| categoria | VARCHAR(50) | |
| descricao | TEXT | |
| local_achado | VARCHAR(100) | |
| data_cadastro | TIMESTAMP WITH TIME ZONE | DEFAULT now() |
| status_atual | VARCHAR(30) | CHECK: ver abaixo |
| foto_url | TEXT | URL pública Supabase Storage (bucket: fotos-itens) |
| caixa_azul | BOOLEAN | DEFAULT false |
| nome_socio_identificado | VARCHAR(100) | |
| titulo_socio | VARCHAR(50) | |
| telefone_socio | VARCHAR(20) | Formato: (21) 99999-9999 |
| contatado | BOOLEAN | DEFAULT false |

**CHECK status_atual:** `'Ativo AeP'`, `'Caixa Azul'`, `'Museu'`, `'A Doar'`, `'Doados'`, `'Descartados'`, `'Devolvidos'`

### Tabela `busca_ativa`
| Coluna | Tipo | Obs |
|--------|------|-----|
| id_ticket | SERIAL PK | |
| nome_socio | VARCHAR(100) NOT NULL | |
| titulo_socio | VARCHAR(50) NOT NULL | |
| telefone | VARCHAR(20) NOT NULL | |
| categoria | VARCHAR(50) NOT NULL | |
| descricao_perdido | TEXT NOT NULL | |
| data_registro | TIMESTAMP WITH TIME ZONE | DEFAULT now() |
| data_limite_retorno | DATE NOT NULL | Cadastro + 10 dias |
| status_busca | VARCHAR(20) | CHECK: 'Aberto', 'Encontrado', 'Encerrado' |

### Tabela `historico_edicoes`
| Coluna | Tipo | Obs |
|--------|------|-----|
| id_edicao | SERIAL PK | |
| codigo_item | VARCHAR(20) | FK → itens |
| campo_alterado | VARCHAR(50) NOT NULL | |
| valor_antigo | TEXT | |
| valor_novo | TEXT | |
| data_hora_alteracao | TIMESTAMP WITH TIME ZONE | DEFAULT now() |
| usuario_editor | VARCHAR(50) NOT NULL | login do usuário |

### Tabela `usuarios`
| Coluna | Tipo | Obs |
|--------|------|-----|
| id | SERIAL PK | |
| login | VARCHAR(50) UNIQUE NOT NULL | |
| nome | VARCHAR(50) NOT NULL | |
| senha | VARCHAR(255) NOT NULL | plaintext por ora — hash futuro |
| perfil | VARCHAR(20) | CHECK: 'Consulta', 'Edicao', 'Admin' |
| criado_em | TIMESTAMP WITH TIME ZONE | DEFAULT now() |

## Categorias e Códigos de Sacolas
| Categoria | Sigla | Capacidade | Códigos |
|-----------|-------|------------|---------|
| Acessórios | AC | 100 | 001AC–100AC |
| Bolas | B | 100 | 001B–100B |
| Bolsas | BOL | 100 | 001BOL–100BOL |
| Brinquedos | BR | 50 | 001BR–050BR |
| Calçados | C | 150 | 001C–150C |
| Cosméticos | CO | 50 | 001CO–050CO |
| Garrafas | G | 150 | 001G–150G |
| Material Esportivo | ME | 100 | 001ME–100ME |
| Objetos | OB | 50 | 001OB–050OB |
| Óculos | OC | 50 | 001OC–050OC |
| Roupas | R | 300 | 001R–300R |
| Toalhas | T | 100 | 001T–100T |

## Regras de Negócio Importantes

### Ciclo de Vida dos Itens
```
Cadastro → Ativo AeP (60 dias)
               ↓ sem busca
           Museu (30 dias)
               ↓ sem busca
           A Doar → Doados (fim)
           Descartados (fim)
               ↓ sócio buscou (qualquer fase)
           Devolvidos (fim)
```
- Movimentações são SEMPRE manuais
- Toda movimentação grava em `historico_edicoes`

### Caixa Azul
- Flag auxiliar independente do status
- Só pode ser marcada quando `status_atual = 'Ativo AeP'`
- Não libera o código da sacola
- Significa que o item está fisicamente separado aguardando retirada

### Transições Permitidas por Status
| Status atual | Pode ir para |
|---|---|
| Ativo AeP | Museu, Devolvidos, A Doar, Descartados |
| Museu | A Doar, Descartados, Devolvidos |
| A Doar | Doados |
| Doados | — (fim) |
| Descartados | — (fim) |
| Devolvidos | — (fim) |

### Confirmação por Senha
Toda edição ou movimentação exige que o usuário digite sua própria senha (validada contra a tabela `usuarios`). Evita alterações acidentais com terminal aberto.

### Dias no Status
Calculado via `historico_edicoes` — usa a data da última alteração de `status_atual`. Se não houver histórico, usa `data_cadastro`.

## Perfis de Usuário
| Perfil | Permissões |
|--------|-----------|
| Consulta | Apenas visualizar |
| Edicao | Visualizar + editar itens + movimentar status |
| Admin | Tudo + tela de configurações |

## CSS Global (app.py)
- Dark mode como padrão (`config.toml`)
- Sidebar: `#141824` (azul quase preto fixo em ambos os temas)
- Cor primária: `#00897b` (verde teal — botões hover, aba ativa)
- Botão Sair: hover vermelho `#cc0000`
- Abas: ativa branca, inativa cinza `#888`

## Seletores CSS Úteis

### Botão Descartar (hover vermelho no dialog)
```css
div[role="dialog"] div[data-testid="stColumn"]:last-child button[data-testid="stBaseButton-secondary"]:hover
```
Pega o botão secondary na última coluna dentro de qualquer st.dialog.

## Próximas Fases
- **Fase 3:** `tela_dashboard.py` — cards de métricas (total itens, busca ativa, SLA vencido), gráficos por categoria e status, monitoramento de SLA
- **Fase 4:** `tela_configuracoes.py` — gestão de usuários (Admin only)
- **Fase 4:** Deploy no Streamlit Community Cloud
- **Pendente:** Bucket `fotos-itens` no Supabase Storage
- **Pendente:** Hash de senha nos usuários
