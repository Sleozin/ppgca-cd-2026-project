# 🎓 PPGCA 2026 — Projeto de Ciência de Dados

> **Mestrado Profissional em Computação Aplicada**
> Prof. Josenildo Silva · IFMA · Turma 2026.1

---

## 👥 Grupo

| Nome | Matrícula | E-mail |
|------|-----------|--------|
| Leonardo dos Santos Pereira | 20261MC.MTC0011 | santos.leonardo@acad.ifma.edu.br |
| Sarah Maciel | 20261MC.MTC0002 | sophia.pinto@acad.ifma.edu.br |

---

## 📋 Sobre o Projeto

> **TODO:** Este algoritmo tem como objetivo a fiscalização do uso de dinheiro publico das emendas parlamentaares
>
> **Pergunta Central:** O algoritmo tem o objetivo de encontrar o padrão medio de valor desempenhado por categoria a fim de encontrar anomalias no uso das emendas, em valores que são muito altos em comparação a media
>
> **Fonte de Dados:** Dados Abertos do Portal da Transparência

---

## 🚀 Como Rodar (Zero Config)

> **Regra de Ouro:** O professor clona este repositório, executa os comandos abaixo
> e tudo funciona. "Funciona na minha máquina" é **falha grave**.

### Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado

### Setup Inicial

```bash
# 1. Clone o repositório
git clone https://github.com/Sleozin/ppgca-cd-2026-project.git
cd ppgca-cd-2026-project

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais (ex: API_KEY)

# 3. Instale as dependências
uv sync
```

### Base de dados e Cabecalhos do .env

- [Acesse Aqui](https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email) para gerar seu token na Api de Dados do Portal da Transparência

```bash
# URL base do Portal da Transparência
API_BASE_URL=https://api.portaldatransparencia.gov.br/api-de-dados/emendas

# Chave de API da fonte de dados escolhida pelo grupo
API_KEY=sua_chave_aqui

# Ano de Pesquisa das emendas
API_YEAR_BASE = seu_ano aqui
```
### Executar o Pipeline Completo

```bash
# Sprint 1 — Ingestão (coleta da API para data/raw)
uv run python src/ingest.py
# Sprint 2 - 
uv run python src/transform.py
# Sprint 3 - 
uv run python src/build_mart.py
uv run quarto render notebooks/eda_modelagem.qmd
```

### Resultado esperado
```
#Apos execução deve aparecer a ingestão de dados, a verificação de qualidade e a analise exploratória de acordo com
ppgca-cd-2026-project/

├── data/                       # Camadas do Data Lake (não versionadas)
│   ├── raw/                    # Dados brutos e imutáveis (JSON)
|       ├── emendas_ano_year-month-day.json # Após Sprint 1
│   ├── trusted/                # Dados validados (Parquet)
│   ├── mart/                   # Tabelas analíticas (Fato/Dimensão)
|       ├── dim_autor.parquet       # Após Sprint 2
|       ├── dim_calendario.parquet  # Após Sprint 2
|       ├── dim_funcao.parquet      # Após Sprint 2
|       ├── dim_localidade.parquet  # Após Sprint 2
|       ├── fato_emendas.parquet    # Após Sprint 2
│   └── feat/                   # Feature Store para ML
├── notebooks/                  # Visualização
│   ├── eda_modelagem_files/    # Scripts de visualização
│   ├── eda_modelagem.html      # Visualização web - Após Sprint 3
│   └── eda_qualidade.qmd       # Após Sprint 2
```

---

## 🏗️ Arquitetura do Projeto

```
ppgca-cd-2026-project/
│
├── src/                        # Código-fonte principal
│   ├── ingest.py               # S1: Coleta da API → data/raw - Desenvolvido ✅
│   ├── transform.py            # S2: Limpeza + Pandera → data/trusted ✅ - Desenvolvido
│   ├── build_mart.py           # S3: Star Schema + Features → data/mart, feat - ✅ - Desenvolvido
│   └── app.py                  # S4: Dashboard Streamlit - Em Desenvolvimento
│
├── data/                       # Camadas do Data Lake (não versionadas)
│   ├── raw/                    # Dados brutos e imutáveis (JSON)
│   ├── trusted/                # Dados validados (Parquet)
│   ├── mart/                   # Tabelas analíticas (Fato/Dimensão)
│   └── feat/                   # Feature Store para ML
│
├── notebooks/                  # Análises exploratórias (EDA)
├── reports/
│   ├── report.qmd              # S4: Relatório Quarto (fonte) - Em Desenvolvimento
|   ├── quality_report.md       # S2: Relatório de Qualidade dos dados - ✅ - Desenvolvido
│   └── data_dictionary.md      # S3: Dicionário de dados (gerado) ✅ - Desenvolvido
│
├── .github/
│   └── workflows/ci.yml        # CI: Verifica reprodutibilidade
│
├── .env.example                # Template de variáveis de ambiente
├── .gitignore                  # Ignora dados, .env, .venv
├── pyproject.toml              # Dependências do projeto (uv)
└── README.md                   # Este arquivo
```

### Fluxo de Dados

```
API/Fonte
    ↓  ingest.py
[data/raw]  ← Imutável. Jamais modificado manualmente.
    ↓  transform.py (DuckDB + Pandera)
[data/trusted]  ← Dado limpo e validado (Parquet).
    ↓  model.py (DuckDB SQL)
[data/mart]     ← Star Schema (BI): fato_principal + dimensões
[data/feat]     ← Feature Store (ML): features.parquet
    ↓  app.py / report.qmd
Dashboard Streamlit + Relatório HTML
```

---

## 🛠️ Stack Tecnológica

| Ferramenta | Papel |
|------------|-------|
| `uv` | Gerenciamento de pacotes e ambiente virtual |
| `DuckDB` | Engine OLAP — processamento analítico local |
| `Pandera` | Contratos de dados e validação de schema |
| `Streamlit` | Data app interativo |
| `Quarto` | Relatório técnico reprodutível |
| `Plotly` | Visualizações interativas |

---

## 📦 Sprints e Entregas

| Sprint | Prazo | Peso | Entrega |
|--------|-------|------|---------|
| **S1 — Infraestrutura** | Semana 02 | 10% | `ingest.py` + repositório configurado | ✅ - Desenvolvido
| **S2 — Qualidade** | Semana 06 | 20% | `transform.py` + `data/trusted/*.parquet` | ✅ - Desenvolvido
| **S3 — Modelagem** | Semana 10 | 25% | `model.py` + Star Schema + Feature Store | ✅ - Desenvolvido
| **S4 — Produto** | Semana 13 | 25% | `app.py` + `reports/report.html` |
| **S5 — Demo Day** | Semana 15 | 20% | Pitch + release v1.0 |

---

## 🔒 Segurança

- **Nunca comite o `.env`** — ele está no `.gitignore`.
- Use `.env.example` como referência para configuração.
- Credenciais (`API_KEY`, senhas) ficam **exclusivamente** no `.env`.

---

## 📚 Referências

- REIS, Joe; HOUSLEY, Matt. *Fundamentals of Data Engineering*. O'Reilly, 2022.
- IGUAL, L.; SEGUÍ, S. *Introduction to Data Science*. Springer, 2017.
- FAWCETT, T.; PROVOST, F. *Data Science para Negócios*. Alta Books, 2016.
- [Documentação DuckDB](https://duckdb.org/docs/)
- [Documentação Streamlit](https://docs.streamlit.io/)
- [Documentação Pandera](https://pandera.readthedocs.io/)
