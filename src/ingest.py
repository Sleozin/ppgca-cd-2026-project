# Script Criado por Leonardo dos Santos Pereira e Sarah Sophia Pinto

import requests
import json
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime


#Carregar variaveis do .env
load_dotenv()
# Função para carregar os dados da fonte
def carrega_dados(ano, url, chave, caminho):
    #Cabecalho da requisição
    headers = {
        "chave-api-dados": chave,
        "accept": "application/json"
    }

    parametros = {"ano": ano, "pagina": 1}
    dados_finais = []

    print(f"Iniciando o carregamento dos dados em {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}")
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
            #Proxima pagina
            parametros["pagina"] += 1
            time.sleep(1) # Respeito ao rate limit da API
            
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {e}")
            break
    if dados_finais:
        # Usando pathlib para lidar com caminhos
        caminho_arquivo = Path(caminho)
        
        # Garante que a pasta (data/raw) exista
        caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_finais, f, ensure_ascii=False, indent=4)
        print(f"\nSucesso! {len(dados_finais)} dados salvos em: '{caminho_arquivo.resolve()}'")
    else:
        print("\nNenhum dado foi baixado.")

if __name__ == "__main__":
    #puxar dados .env
    KEY = os.getenv("API_KEY")
    URL = os.getenv("API_BASE_URL")
    ANO = os.getenv("API_YEAR_BASE")

    if not KEY:
        print("Configure a Chave da API no .env")
    else:
        data_atual = datetime.now().strftime("%Y-%m-%d")
        caminho_final = Path(f"data/raw/emendas_{ANO}_{data_atual}.json")
        # Verificando se coleta já ocorreu
        if caminho_final.exists():
            print(f"Atenção: A coleta de hoje já foi realizada!")
            print(f"O arquivo já se encontra em: {caminho_final}")
        else:
            carrega_dados(ANO, URL, KEY, caminho=caminho_final)

