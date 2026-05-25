"""
transform.py

Sprint 2 — Qualidade & Trusted Layer

Pipeline ETL completo:

1. Lê JSON da camada RAW
2. Padroniza colunas
3. Corrige tipos
4. Trata valores nulos
5. Remove duplicatas
6. Identifica registros inválidos
7. Aplica contrato de dados (Pandera)
8. Salva camada Trusted
9. Salva registros inválidos (Quarantine)
10. Gera relatório de qualidade

Execução:

uv run python src/transform.py
"""

# =========================================================
# IMPORTS
# =========================================================

import sys
from pathlib import Path

# adiciona raiz do projeto ao PYTHONPATH
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from datetime import datetime

import pandas as pd
import pandera.pandas as pa

from schemas.schema import schema


# =========================================================
# CAMINHOS
# =========================================================

RAW_PATH = Path(
    "data/raw/emendas_2024_2026-05-25.json"
)

TRUSTED_PATH = Path(
    "data/trusted/emendas_trusted.parquet"
)

QUARANTINE_PATH = Path(
    "data/quarantine/emendas_invalidas.parquet"
)

REPORT_PATH = Path(
    "reports/quality_report.md"
)


# =========================================================
# LEITURA DOS DADOS
# =========================================================

def load_data() -> pd.DataFrame:
    """
    Lê arquivo JSON da camada RAW.
    """

    print("Lendo arquivo JSON...")

    try:

        # JSON comum
        df = pd.read_json(RAW_PATH)

    except ValueError:

        # JSON Lines
        df = pd.read_json(
            RAW_PATH,
            lines=True
        )

    print(f"Total de registros lidos: {len(df)}")

    return df


# =========================================================
# PADRONIZAÇÃO DAS COLUNAS
# =========================================================

def normalize_columns(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Padroniza nomes das colunas.
    """

    print("Padronizando nomes das colunas...")

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    return df


# =========================================================
# CORREÇÃO DE TIPOS
# =========================================================

def correct_data_types(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Corrige tipos dos dados.
    """

    print("Corrigindo tipos...")

    # =====================================================
    # COLUNAS NUMÉRICAS
    # =====================================================

    colunas_numericas = [
        "ano",
        "valorempenhado",
        "valorliquidado",
        "valorpago",
        "valorrestoinscrito",
        "valorrestocancelado",
        "valorrestopago"
    ]

    for coluna in colunas_numericas:

        if coluna in df.columns:

            df[coluna] = pd.to_numeric(
                df[coluna],
                errors="coerce"
            )

    # =====================================================
    # COLUNAS TEXTUAIS
    # =====================================================

    colunas_texto = [
        "codigoemenda",
        "tipoemenda",
        "autor",
        "nomeautor",
        "numeroemenda",
        "localidadedogasto",
        "funcao",
        "subfuncao"
    ]

    for coluna in colunas_texto:

        if coluna in df.columns:

            df[coluna] = (
                df[coluna]
                .astype("string")
            )

    return df

# =========================================================
# TRATAMENTO DE NULOS
# =========================================================

def handle_nulls(
    df: pd.DataFrame
):
    """
    Trata valores nulos.
    """

    print("Tratando valores nulos...")

    before = len(df)

    # remove registros sem código
    df = df.dropna(
        subset=["codigoemenda"]
    )

    removed = before - len(df)

    print(
        f"Nulos removidos: {removed}"
    )

    return df, removed


# =========================================================
# REMOÇÃO DE DUPLICATAS
# =========================================================

def remove_duplicates(
    df: pd.DataFrame
):
    """
    Remove duplicatas.
    """

    print("Removendo duplicatas...")

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    print(
        f"Duplicatas removidas: {removed}"
    )

    return df, removed


# =========================================================
# IDENTIFICAÇÃO DE INVÁLIDOS
# =========================================================

def separate_invalid_records(
    df: pd.DataFrame
):
    """
    Identifica registros inválidos.
    """

    print(
        "Separando registros inválidos..."
    )

    invalid_mask = pd.Series(
        False,
        index=df.index
    )

    # =====================================================
    # VALORES NEGATIVOS
    # =====================================================

    colunas_valores = [
        "valorempenhado",
        "valorliquidado",
        "valorpago",
        "valorrestoinscrito",
        "valorrestocancelado",
        "valorrestopago"
    ]

    for coluna in colunas_valores:

        if coluna in df.columns:

            invalid_mask |= (
                df[coluna] < 0
            )

    # =====================================================
    # ANOS INVÁLIDOS
    # =====================================================

    if "ano" in df.columns:

        invalid_mask |= (
            (df["ano"] < 2024)
            |
            (df["ano"] > 2026)
        )

    invalid_df = df[invalid_mask]

    valid_df = df[~invalid_mask]

    print(
        f"Registros inválidos: "
        f"{len(invalid_df)}"
    )

    return valid_df, invalid_df


# =========================================================
# VALIDAÇÃO COM PANDERA
# =========================================================

def validate_schema(
    df: pd.DataFrame
):
    """
    Aplica contrato de dados.
    """

    print(
        "Aplicando contrato de dados..."
    )

    schema.validate(df)

    print(
        "Schema validado com sucesso."
    )


# =========================================================
# SALVAR TRUSTED
# =========================================================

def save_trusted(
    df: pd.DataFrame
):
    """
    Salva camada trusted.
    """

    print(
        "Salvando camada trusted..."
    )

    TRUSTED_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(
        TRUSTED_PATH,
        index=False
    )


# =========================================================
# SALVAR QUARENTENA
# =========================================================

def save_quarantine(
    df: pd.DataFrame
):
    """
    Salva registros inválidos.
    """

    print(
        "Salvando quarentena..."
    )

    QUARANTINE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(
        QUARANTINE_PATH,
        index=False
    )


# =========================================================
# GERAR RELATÓRIO
# =========================================================

def generate_report(
    total_lidos,
    total_validos,
    total_invalidos,
    nulls_removed,
    duplicates_removed
):
    """
    Gera relatório markdown.
    """

    print(
        "Gerando relatório..."
    )

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report = f"""
# Quality Report

## Data de execução

{datetime.now()}

---

# Estatísticas Gerais

- Registros lidos: {total_lidos}
- Registros válidos: {total_validos}
- Registros inválidos: {total_invalidos}

---

# Problemas Identificados

## Valores nulos removidos

- {nulls_removed}

## Duplicatas removidas

- {duplicates_removed}

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
"""

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report)


# =========================================================
# PIPELINE PRINCIPAL
# =========================================================

def main():

    print("=" * 50)
    print("INICIANDO TRANSFORMAÇÃO")
    print("=" * 50)

    # =====================================================
    # LEITURA
    # =====================================================

    df = load_data()

    total_lidos = len(df)

    # =====================================================
    # PADRONIZAÇÃO
    # =====================================================

    df = normalize_columns(df)

    # =====================================================
    # TIPOS
    # =====================================================

    df = correct_data_types(df)

    # =====================================================
    # NULOS
    # =====================================================

    df, nulls_removed = handle_nulls(df)

    # =====================================================
    # DUPLICATAS
    # =====================================================

    df, duplicates_removed = (
        remove_duplicates(df)
    )

    # =====================================================
    # REGISTROS INVÁLIDOS
    # =====================================================

    valid_df, invalid_df = (
        separate_invalid_records(df)
    )

    total_validos = len(valid_df)

    total_invalidos = len(invalid_df)

    # =====================================================
    # VALIDAÇÃO
    # =====================================================

    validate_schema(valid_df)

    # =====================================================
    # SALVAMENTO
    # =====================================================

    save_trusted(valid_df)

    save_quarantine(invalid_df)

    # =====================================================
    # RELATÓRIO
    # =====================================================

    generate_report(
        total_lidos,
        total_validos,
        total_invalidos,
        nulls_removed,
        duplicates_removed
    )

    print("=" * 50)
    print("PIPELINE FINALIZADA")
    print("=" * 50)


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    main()