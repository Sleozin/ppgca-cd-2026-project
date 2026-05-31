
# Quality Report

## Data de execução

2026-05-30 01:28:32.018304

---

# Estatísticas Gerais

- Registros lidos: 5653
- Registros válidos: 5653
- Registros inválidos: 0

---

# Problemas Identificados

## Valores nulos removidos

- 0

## Duplicatas removidas

- 0

---

# Estratégias Aplicadas

- Padronização de colunas
- Correção de tipos
- Tratamento de nulos
- Remoção de duplicatas
- Validação declarativa com Pandera
- Quarentena de registros inválidos
- Escrita em formato Parquet

---

# Camadas Geradas

## Trusted

data/trusted/emendas_trusted.parquet

## Quarantine

data/quarantine/emendas_invalidas.parquet
