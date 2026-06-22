# Script Criado por Leonardo dos Santos Pereira e Sarah Sophia Pinto

import duckdb
from pathlib import Path
import time

def build_mart():
    trusted_dir = Path("data/trusted")
    mart_dir = Path("data/mart")
    
    # Garante a existência do diretório
    mart_dir.mkdir(parents=True, exist_ok=True)

    # Verifica se os dados da camada trusted existem
    trusted_file = trusted_dir / "emendas_trusted.parquet"
    if not trusted_file.exists():
        print(f"Arquivo não encontrado: {trusted_file}. Execute transform.py primeiro.")
        return

    # Inicia o motor analítico DuckDB em memória
    con = duckdb.connect(database=':memory:')
    
    print("Iniciando a modelagem dimensional (Star Schema) via DuckDB...")
    start_time = time.time()

    try:
        # Carrega o parquet da camada trusted em uma view unificada
        con.execute(f"CREATE OR REPLACE VIEW base_emendas AS SELECT * FROM '{trusted_file}'")
        
        # 1. Dimensão Autor
        con.execute("""
            CREATE OR REPLACE TABLE dim_autor AS
            SELECT DISTINCT
                MD5(CAST(nomeautor AS VARCHAR)) AS sk_autor,
                nomeautor AS nome_autor,
                autor AS grupo_autor,
                tipoemenda AS tipo_emenda
            FROM base_emendas
            WHERE nomeautor IS NOT NULL
        """)

        # 2. Dimensão Função (Área de Aplicação)
        con.execute("""
            CREATE OR REPLACE TABLE dim_funcao AS
            SELECT DISTINCT
                MD5(CAST(funcao AS VARCHAR) || CAST(subfuncao AS VARCHAR)) AS sk_funcao,
                funcao,
                subfuncao
            FROM base_emendas
            WHERE funcao IS NOT NULL
        """)

        # 3. Dimensão Localidade
        con.execute("""
            CREATE OR REPLACE TABLE dim_localidade AS
            SELECT DISTINCT
                MD5(CAST(localidadedogasto AS VARCHAR)) AS sk_localidade,
                localidadedogasto AS localidade_gasto
            FROM base_emendas
            WHERE localidadedogasto IS NOT NULL
        """)

        # 4. Dimensão Calendário (Gerada programaticamente)
        # Como o dado só possui "ano", geramos o primeiro dia do ano respectivo para manter
        # compatibilidade com ferramentas de BI e Window Functions temporais no DuckDB.
        con.execute("""
            CREATE OR REPLACE TABLE dim_calendario AS
            WITH limites AS (
                SELECT 
                    MAKE_DATE(MIN(CAST(ano AS INTEGER)), 1, 1) AS data_min,
                    MAKE_DATE(MAX(CAST(ano AS INTEGER)), 12, 31) AS data_max
                FROM base_emendas
                WHERE ano IS NOT NULL
            )
            SELECT
                CAST(data_gerada AS DATE) AS sk_data,
                EXTRACT(YEAR FROM data_gerada) AS ano,
                EXTRACT(MONTH FROM data_gerada) AS mes,
                EXTRACT(DAY FROM data_gerada) AS dia,
                EXTRACT(QUARTER FROM data_gerada) AS trimestre,
                DAYNAME(data_gerada) AS dia_semana
            FROM limites,
            UNNEST(GENERATE_SERIES(data_min, data_max, INTERVAL 1 DAY)) AS t(data_gerada)
        """)

        # 5. Tabela Fato
        con.execute("""
            CREATE OR REPLACE TABLE fato_emendas AS
            SELECT
                MD5(CAST(codigoemenda AS VARCHAR)) AS sk_emenda,
                MD5(CAST(nomeautor AS VARCHAR)) AS fk_autor,
                MD5(CAST(funcao AS VARCHAR) || CAST(subfuncao AS VARCHAR)) AS fk_funcao,
                MD5(CAST(localidadedogasto AS VARCHAR)) AS fk_localidade,
                
                -- Associa ao primeiro dia do ano correspondente à emenda para ligar à dim_calendario
                MAKE_DATE(CAST(ano AS INTEGER), 1, 1) AS fk_data,
                
                -- Atributos de Degeneração (identificadores nativos)
                codigoemenda AS codigo_emenda,
                numeroemenda AS numero_emenda,
                
                -- Métricas Base (Valores já tratados no transform.py)
                COALESCE(valorempenhado, 0) AS valor_empenhado,
                COALESCE(valorliquidado, 0) AS valor_liquidado,
                COALESCE(valorpago, 0) AS valor_pago,
                COALESCE(valorrestoinscrito, 0) AS valor_resto_inscrito,
                
                -- KPI 1: Valor Pago em Milhões
                (COALESCE(valorpago, 0) / 1000000.0) AS kpi_pago_milhoes,
                
                -- KPI 2: Taxa de Pagamento (Qual percentual do que foi empenhado foi efetivamente pago)
                CASE 
                    WHEN valorempenhado > 0 THEN (valorpago / valorempenhado) 
                    ELSE 0 
                END AS kpi_taxa_pagamento
                
            FROM base_emendas
            WHERE codigoemenda IS NOT NULL
        """)

        # Exportação para Parquet e Resumo
        tabelas = ['dim_autor', 'dim_funcao', 'dim_localidade', 'dim_calendario', 'fato_emendas']
        
        print("\n" + "="*50)
        print("RESUMO DA CONSTRUÇÃO DO MART")
        print("="*50)
        
        for tabela in tabelas:
            caminho_saida = mart_dir / f"{tabela}.parquet"
            
            # Gravação em Parquet via DuckDB
            con.execute(f"COPY {tabela} TO '{caminho_saida}' (FORMAT PARQUET)")
            
            # Contagem para o terminal
            linhas = con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
            print(f"[OK] {tabela}.parquet gerado com {linhas} linhas.")

        print("-" * 50)
        print(f"Total de tabelas geradas: {len(tabelas)}")
        print(f"Tempo de processamento: {time.time() - start_time:.2f} segundos")
        print(f"Artefatos disponíveis em: {mart_dir.resolve()}")

    except Exception as e:
        print(f"Erro durante a modelagem com DuckDB: {e}")

if __name__ == "__main__":
    build_mart()