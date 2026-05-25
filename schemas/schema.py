"""
schema.py

Contrato de dados da camada Trusted.
"""

import pandera.pandas as pa

from pandera import Column, Check


schema = pa.DataFrameSchema({

    # ==================================================
    # Código da emenda
    # ==================================================

    "codigoemenda": Column(
        str,
        nullable=False
    ),

    # ==================================================
    # Ano da emenda
    # ==================================================

    "ano": Column(
        int,
        nullable=False,
        checks=Check.in_range(2024, 2026)
    ),

    # ==================================================
    # Tipo da emenda
    # ==================================================

    "tipoemenda": Column(
        str,
        nullable=True
    ),

    # ==================================================
    # Autor
    # ==================================================

    "autor": Column(
        str,
        nullable=True
    ),

    # ==================================================
    # Nome do autor
    # ==================================================

    "nomeautor": Column(
        str,
        nullable=True
    ),

    # ==================================================
    # Número da emenda
    # ==================================================

    "numeroemenda": Column(
        str,
        nullable=True
    ),

    # ==================================================
    # Localidade do gasto
    # ==================================================

    "localidadedogasto": Column(
        str,
        nullable=True
    ),

    # ==================================================
    # Função
    # ==================================================

    "funcao": Column(
        str,
        nullable=True
    ),

    # ==================================================
    # Subfunção
    # ==================================================

    "subfuncao": Column(
        str,
        nullable=True
    ),

    # ==================================================
    # Valores monetários
    # ==================================================

    "valorempenhado": Column(
        float,
        nullable=True,
        checks=Check.ge(0)
    ),

    "valorliquidado": Column(
        float,
        nullable=True,
        checks=Check.ge(0)
    ),

    "valorpago": Column(
        float,
        nullable=True,
        checks=Check.ge(0)
    ),

    "valorrestoinscrito": Column(
        float,
        nullable=True,
        checks=Check.ge(0)
    ),

    "valorrestocancelado": Column(
        float,
        nullable=True,
        checks=Check.ge(0)
    ),

    "valorrestopago": Column(
        float,
        nullable=True,
        checks=Check.ge(0)
    ),
})