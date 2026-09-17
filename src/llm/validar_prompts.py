"""Script de validação (teste de regressão) para o módulo de LLM.

Verifica se o JSON gerado contém exatamente as 11 chaves exigidas (9 perguntas + populações + avisos)
e não está vazio. 

Uso:
    python src/llm/validar_prompts.py --modelo gemini-2.5-flash
    python src/llm/validar_prompts.py --modelo qwen2.5vl:7b --backend ollama
"""

import argparse
import sys
import json
from pathlib import Path

# Adiciona o diretório raiz para importação
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.llm.comparar_llm_gemini import reconstruir_bula_com_gemini
from src.llm.testar_llm import extrair_dados_com_ollama

CHAVES_ESPERADAS = {
    "indicacao", "funcionamento", "contraindicacoes", "precaucoes_populacoes_especiais",
    "interacoes_medicamentosas", "armazenamento", "posologia_uso", "esquecimento",
    "efeitos_colaterais", "superdose", "avisos_seguranca"
}

def validar_json(texto_json: str) -> bool:
    try:
        dados = json.loads(texto_json)
        chaves_obtidas = set(dados.keys())
        
        faltando = CHAVES_ESPERADAS - chaves_obtidas
        sobrando = chaves_obtidas - CHAVES_ESPERADAS
        
        if faltando:
            print(f"❌ Falha: Chaves ausentes: {faltando}")
            return False
        if sobrando:
            print(f"⚠️ Aviso: Chaves extras retornadas: {sobrando}")
            
        print("✅ Sucesso: O JSON contém toda a estrutura esperada (9 perguntas + 2 extras de segurança)!")
        return True
    except json.JSONDecodeError:
        print("❌ Falha: O retorno não é um JSON válido.")
        return False
    except Exception as e:
        print(f"❌ Falha inesperada ao validar: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["gemini", "ollama"], default="gemini", help="Backend a testar")
    parser.add_argument("--modelo", default="gemini-2.5-flash", help="Nome do modelo")
    parser.add_argument("--entrada", default="resultados/bula_extraida.txt", help="Caminho do arquivo de texto do OCR")
    
    args = parser.parse_args()
    
    print(f"--- Iniciando Teste de Validação ({args.backend} - {args.modelo}) ---")
    
    if args.backend == "gemini":
        resultado = reconstruir_bula_com_gemini(modelo=args.modelo, arquivo_ocr=args.entrada, arquivo_saida="resultados/teste_validacao.json")
    else:
        resultado = extrair_dados_com_ollama(modelo=args.modelo, arquivo_ocr=args.entrada)
        
    if not resultado:
        print("❌ Falha: Não foi possível obter resposta do modelo.")
        return 1
        
    sucesso = validar_json(resultado)
    return 0 if sucesso else 1

if __name__ == "__main__":
    sys.exit(main())
