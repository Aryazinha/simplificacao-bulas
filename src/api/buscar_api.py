import requests
import sys
import pdfplumber
from deep_translator import GoogleTranslator

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def traduzir_texto(texto: str) -> str:
    try:
        texto_traduzido = GoogleTranslator(source='en', target='pt').translate(texto)
        return texto_traduzido
    except Exception as e:
        print(f"Erro ao traduzir o texto: {e}")
        return texto

def buscar_bula_api(nome_ingles: str, nome_portugues: str) -> dict:
    url = f'https://api.fda.gov/drug/label.json?search=active_ingredient:"{nome_ingles}"&limit=1'

    try:
        resposta = requests.get(url)
        resposta.raise_for_status()  

        dados_json = resposta.json()
        resultados = dados_json.get('results', [])

        if resultados:
            resultado = resultados[0]

            proposito_en = resultado.get('purpose', ['Não disponível'])[0]
            indicacoes_en = resultado.get('indications_and_usage', ['Não disponível'])[0]
            contraindicacoes_en = resultado.get('do_not_use', ['Não disponível'])[0]
            advertencias_en = resultado.get('warnings', ['Não disponível'])[0]
            parar_uso_en = resultado.get('stop_use', ['Não disponível'])[0]

            proposito_pt = traduzir_texto(proposito_en)
            indicacoes_pt = traduzir_texto(indicacoes_en)
            contraindicacoes_pt = traduzir_texto(contraindicacoes_en)
            advertencias_pt = traduzir_texto(advertencias_en)
            parar_uso_pt = traduzir_texto(parar_uso_en)

            print("=========================================")
            print("DADOS RECEBIDOS DA API COM SUCESSO!")
            print("=========================================")
            print(f"> PRINCÍPIO ATIVO ENCONTRADO:\n{nome_portugues} ({nome_ingles})\n")
            print(f"> PROPÓSITO:\n{proposito_pt}\n")
            print(f"> INDICAÇÕES DE USO:\n{indicacoes_pt}\n")
            print(f"> CONTRAINDICAÇÕES:\n{contraindicacoes_pt}\n")
            print(f"> ADVERTÊNCIAS:\n{advertencias_pt}\n")
            print(f"> PARAR USO:\n{parar_uso_pt}")
            print("=========================================")
            
            return resultado 
        else:
            print("A API respondeu, mas não encontrou resultados para este medicamento.")
            return {}

    except requests.RequestException as e:
        print(f"Falha na conexão: {e}")
        return {}
    

def extrair_texto_bula(caminho_pdf: str) -> str:
    texto_completo = ""
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto_pagina = pagina.extract_text()
                
                if texto_pagina:
                    texto_completo += texto_pagina + "\n\n"
        return texto_completo
        
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_pdf}' não foi encontrado na pasta")
        return ""
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
        return ""

if __name__ == "__main__":

    # Analgésicos e Anti-inflamatórios:
    # - "aspirin" / "Aspirina"
    # - "naproxen" / "Naproxeno"
    # - "diclofenac" / "Diclofenaco"
    #
    # Antialérgicos:
    # - "loratadine" / "Loratadina"
    # - "cetirizine" / "Cetirizina"
    # - "diphenhydramine" / "Difenidramina"
    #
    # Estômago e Intestino:
    # - "omeprazole" / "Omeprazol"
    # - "simethicone" / "Simeticona"
    # - "loperamide" / "Loperamida"
    # - "bismuth subsalicylate" / "Subsalicilato de Bismuto"
    #
    # Sistema Respiratório e Tosse:
    # - "guaifenesin" / "Guaifenesina"
    # - "dextromethorphan" / "Dextrometorfano"
    #
    # Obs: Medicamentos não aprovados nos EUA (como a Dipirona/metamizole)
    # não retornarão resultados nesta API.

    dados_da_bula = buscar_bula_api("omeprazole", "Omeprazol")

    #dados_da_bula_anvisa = extrair_texto_bula("dados/entrada/bula_paciente.pdf")
    #if dados_da_bula_anvisa:
    #    print("\n[INFO] Dados extraídos da bula do paciente:")
    #    print("=========================================")
    #    print(dados_da_bula_anvisa)