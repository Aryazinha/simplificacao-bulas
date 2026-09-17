"""Reconstrói, via Gemini, o texto de bula extraído pelo OCR.

A chave é lida da variável de ambiente GEMINI_API_KEY; se não estiver no ambiente,
o arquivo .env da raiz do projeto é carregado. O modelo pode ser trocado por
GEMINI_MODEL ou por --modelo.

Exemplo:
    python src/llm/comparar_llm_gemini.py
"""

import os
import sys
import json
from pathlib import Path

from google import genai
from google.genai import types

# O pyproject.toml cuida de colocar src no PYTHONPATH.
from src.core.llm.prompts import montar_prompt_simplificacao
from src.core.modelos.bula import BulaSimplificada

RAIZ = Path(__file__).resolve().parents[2]
MODELO_PADRAO = "gemini-2.5-flash"
ENTRADA_PADRAO = "resultados/bula_extraida.txt"
SAIDA_PADRAO = "resultados/resultado_gemini.json"

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def caminho(valor: str) -> Path:
    p = Path(valor)
    return p if p.is_absolute() else RAIZ / p


def carregar_env() -> None:
    """Lê o .env da raiz sem sobrescrever variáveis já definidas no ambiente."""
    arquivo = RAIZ / ".env"
    if not arquivo.exists():
        return

    # Lemos linha a linha do .env e populamos os.environ manualmente
    # Isso permite usar variáveis sensíveis (API Keys) sem commitá-las no código fonte.
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        chave = chave.strip()
        # Removemos aspas duplas ou simples que as pessoas costumam colocar no .env
        valor = valor.strip().strip('"').strip("'")
        if chave and chave not in os.environ:
            os.environ[chave] = valor


def reconstruir_bula_com_gemini(
    modelo: str = MODELO_PADRAO,
    arquivo_ocr: str = ENTRADA_PADRAO,
    arquivo_saida: str = SAIDA_PADRAO,
) -> str | None:
    carregar_env()
    chave_api = os.environ.get("GEMINI_API_KEY", "").strip()

    if not chave_api:
        print(
            "Erro: defina GEMINI_API_KEY no ambiente ou no arquivo .env da raiz "
            "(copie .env.example para .env)."
        )
        return None

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
        # Instanciação simplificada do GenAI. O SDK novo abstrai toda a camada REST e chamadas HTTP.
        client = genai.Client(api_key=chave_api)
        
        # generate_content faz a chamada efetiva à API. O schema força a saída em JSON tipado.
        resposta = client.models.generate_content(
            model=modelo,
            contents=montar_prompt_simplificacao(texto_bula),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BulaSimplificada,
                temperature=0.1,  # Baixa temperatura para minimizar alucinações (foco determinístico)
            ),
        )
    except Exception as e:
        print(f"Erro ao se comunicar com o Gemini: {e}")
        return None

    texto_resposta = (resposta.text or "").strip()
    if not texto_resposta:
        print("O Gemini retornou uma resposta vazia.")
        return None

    try:
        # Converte a resposta em string para dicionário e depois refaz em JSON bonito (indent=2)
        json_obj = json.loads(texto_resposta)
        texto_resposta = json.dumps(json_obj, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        print("Aviso: O modelo não retornou um JSON válido.")

    destino = caminho(arquivo_saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto_resposta, encoding="utf-8")

    print(f"Resultado salvo em '{destino}'")
    return texto_resposta

