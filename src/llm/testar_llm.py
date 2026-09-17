"""Reconstrói, via Ollama local, o texto de bula extraído pelo OCR.

Sem argumentos, pergunta o modelo no terminal; com --modelo, roda sem interação.

Exemplos:
    python src/llm/testar_llm.py
    python src/llm/testar_llm.py --modelo qwen2.5vl:7b
"""

import argparse
import sys
import json
import re
from pathlib import Path

import ollama

# Importa o novo módulo de prompts compartilhado
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.llm.prompts import montar_prompt_simplificacao

RAIZ = Path(__file__).resolve().parents[2]
ENTRADA_PADRAO = "resultados/bula_extraida.txt"
PASTA_SAIDA = "resultados"

MODELOS = {
    "1": "qwen2.5vl:7b",
    "2": "llama3.2",
    "3": "granite3.2",
}

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def caminho(*partes: str) -> Path:
    """Resolve caminhos relativos a partir da raiz do projeto, não do cwd."""
    p = Path(*partes)
    return p if p.is_absolute() else RAIZ / p


def escolher_modelo_ollama() -> str | None:
    print("Modelos disponíveis no Ollama:")
    for opcao, nome in MODELOS.items():
        print(f"{opcao} - {nome}")

    escolha = input("Escolha um modelo: ").strip()

    if escolha not in MODELOS:
        print("Opção inválida.")
        return None

    return MODELOS[escolha]


def extrair_dados_com_ollama(modelo: str, arquivo_ocr: str = ENTRADA_PADRAO) -> str | None:
    print(f"Modelo escolhido: {modelo}")

    caminho_ocr = caminho(arquivo_ocr)
    if not caminho_ocr.exists():
        print(f"Arquivo '{caminho_ocr}' não encontrado. Execute o OCR primeiro.")
        return None

    texto_bula = caminho_ocr.read_text(encoding="utf-8")
    if not texto_bula.strip():
        print(f"Arquivo '{caminho_ocr}' está vazio.")
        return None

    print(f"Enviando texto para o modelo '{modelo}' usando o prompt centralizado...")

    try:
        # ollama.chat suporta format="json" em versões recentes
        resposta = ollama.chat(
            model=modelo,
            messages=[{"role": "user", "content": montar_prompt_simplificacao(texto_bula)}],
            format="json",
            options={"temperature": 0.1}
        )
    except Exception as e:
        print(f"Erro ao se comunicar com o Ollama: {e}")
        return None

    texto_resposta = resposta["message"]["content"].strip()
    if not texto_resposta:
        print("O modelo retornou uma resposta vazia.")
        return None

    # Tenta limpar e reformatar o JSON para garantir legibilidade
    try:
        # Tenta encontrar bloco json caso o modelo tenha ignorado format="json"
        match = re.search(r'```json\s*(.*?)\s*```', texto_resposta, re.DOTALL)
        if match:
            texto_resposta = match.group(1)
        
        json_obj = json.loads(texto_resposta)
        texto_resposta = json.dumps(json_obj, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        print("Aviso: O modelo não retornou um JSON válido.")

    sufixo = modelo.replace(":", "_").replace(".", "_")
    destino = caminho(PASTA_SAIDA, f"resultado_ollama_{sufixo}.json")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto_resposta, encoding="utf-8")

    print(f"Resultado salvo em '{destino}'")
    return texto_resposta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--modelo",
        help=f"Nome do modelo no Ollama. Sugestões: {', '.join(MODELOS.values())}.",
    )
    parser.add_argument("--entrada", default=ENTRADA_PADRAO, help="Texto extraído pelo OCR.")
    args = parser.parse_args()

    modelo = args.modelo or escolher_modelo_ollama()
    if not modelo:
        print("Nenhum modelo válido foi escolhido.")
        return 1

    resultado = extrair_dados_com_ollama(modelo, args.entrada)
    if not resultado:
        return 1

    print("\n===== BULA SIMPLIFICADA E ESTRUTURADA (JSON) =====\n")
    print(resultado)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
