
# Quality Report

## Data de execução

2026-06-21 23:09:55.684768

---

# Estatísticas Gerais

- Registros lidos: 6990
- Registros válidos: 6990
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
