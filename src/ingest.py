# Script Criado por Leonardo dos Santos Pereira e Sarah Sophia Pinto

import requests
import json
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Carregar variaveis do .env
load_dotenv()

def dados_sao_identicos(dados_novos, dados_existentes):
    """
    Verifica se dois conjuntos de dados JSON (listas de dicionários) são idênticos.
    Ordena os registros para evitar falsos negativos causados por mudanças 
    na ordem em que a API retorna as páginas.
    """
    # Se o tamanho for diferente, já sabemos que os dados mudaram
    if len(dados_novos) != len(dados_existentes):
        return False
        
    # Converte cada dicionário da lista em uma string JSON padronizada (com chaves ordenadas)
    # Em seguida, ordena a lista inteira. Isso garante que a comparação funcione 
    # independentemente de como a API ordenou os registros no momento do request.
    lista_nova_ordenada = sorted([json.dumps(item, sort_keys=True) for item in dados_novos])
    lista_exist_ordenada = sorted([json.dumps(item, sort_keys=True) for item in dados_existentes])
    
    return lista_nova_ordenada == lista_exist_ordenada

# Função para carregar os dados da fonte
def carrega_dados(ano, url, chave, caminho):
    # Cabecalho da requisição
    headers = {
        "chave-api-dados": chave,
        "accept": "application/json"
    }

    parametros = {"ano": ano, "pagina": 1}
    dados_finais = []

    print(f"Iniciando o carregamento dos dados em {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    
    while True:
        # Tratamento da resposta, Api processa com estrutura pagina por pagina
        try:
            response = requests.get(url, headers=headers, params=parametros, timeout=10)
            if response.status_code != 200:
                print(f"Erro na API: {response.status_code} - {response.text}")
                break
            
            dados = response.json()
            if not dados:
                break
                
            dados_finais.extend(dados)
            print(f"Página {parametros['pagina']} concluída. (Total: {len(dados_finais)} registros)")
            
            # Proxima pagina
            parametros["pagina"] += 1
            time.sleep(1) # Respeito ao rate limit da API
            
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {e}")
            break
            
    if dados_finais:
        caminho_arquivo = Path(caminho)
        
        # Verificação de Idempotência (Comparação Profunda)
        if caminho_arquivo.exists():
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados_existentes = json.load(f)
                
                # Usa a nova função para comparar o conteúdo real
                if dados_sao_identicos(dados_finais, dados_existentes):
                    print(f"\nIdempotência: O arquivo '{caminho_arquivo.resolve()}' já possui exatamente os mesmos dados. Nenhuma alteração foi gravada.")
                    return
            except (json.JSONDecodeError, IOError):
                print("\nArquivo existente corrompido ou inacessível. O arquivo será sobrescrito.")

        # Garante que a pasta (data/raw) exista
        caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_finais, f, ensure_ascii=False, indent=4)
            
        print(f"\nSucesso! {len(dados_finais)} dados salvos em: '{caminho_arquivo.resolve()}'")
    else:
        print("\nNenhum dado foi baixado.")

if __name__ == "__main__":
    # puxar dados .env
    KEY = os.getenv("API_KEY")
    URL = os.getenv("API_BASE_URL")
    ANO = os.getenv("API_YEAR_BASE")

    # Solicitar token no terminal caso não exista no .env
    if not KEY:
        print("Chave da API não encontrada no arquivo .env.")
        KEY = input("Por favor, insira o token do Portal da Transparência: ").strip()

    if not KEY:
        print("Nenhuma chave foi fornecida. Encerrando a execução.")
    elif not URL or not ANO:
        print("Certifique-se de que API_BASE_URL e API_YEAR_BASE estejam configurados no .env.")
    else:
        data_atual = datetime.now().strftime("%Y-%m-%d")
        caminho_final = Path(f"data/raw/emendas_{ANO}_{data_atual}.json")
        carrega_dados(ANO, URL, KEY, caminho=caminho_final)