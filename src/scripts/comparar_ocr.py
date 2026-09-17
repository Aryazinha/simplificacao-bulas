"""Mede o CER do texto bruto do OCR contra o gabarito.

Exemplos:
    python src/comparacao/comparar_ocr.py
    python src/comparacao/comparar_ocr.py --ocr resultados/bula_extraida.txt --bruto
"""

import argparse
import sys
from pathlib import Path

from jiwer import cer

# Reaproveita a normalização usada na comparação das LLMs, para que os dois números
# (OCR e LLM) sejam calculados sobre o mesmo tratamento de texto.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comparar_llm import caminho, normalizar  # noqa: E402

OCR_PADRAO = "resultados/bula_extraida.txt"
GABARITO_PADRAO = "dados/gabarito/bula_gabarito.txt"

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def comparar_textos(
    arquivo_ocr: str = OCR_PADRAO,
    arquivo_gabarito: str = GABARITO_PADRAO,
    normalizado: bool = True,
) -> tuple[float, float]:
    """Retorna (precisão em %, CER) entre o texto do OCR e o gabarito."""
    caminho_ocr = caminho(arquivo_ocr)
    caminho_gabarito = caminho(arquivo_gabarito)

    for alvo in (caminho_ocr, caminho_gabarito):
        if not alvo.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {alvo}")

    texto_ocr = caminho_ocr.read_text(encoding="utf-8")
    texto_gabarito = caminho_gabarito.read_text(encoding="utf-8")

    if normalizado:
        texto_ocr = normalizar(texto_ocr)
        texto_gabarito = normalizar(texto_gabarito)

    if not texto_gabarito:
        raise ValueError(f"Gabarito vazio: {caminho_gabarito}")

    print(f"Gabarito: {len(texto_gabarito)} caracteres")
    print(f"OCR: {len(texto_ocr)} caracteres")

    taxa_erro = cer(texto_gabarito, texto_ocr)
    precisao = (1 - taxa_erro) * 100

    return precisao, taxa_erro


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ocr", default=OCR_PADRAO, help="Arquivo com o texto extraído.")
    parser.add_argument("--gabarito", default=GABARITO_PADRAO, help="Arquivo de referência.")
    parser.add_argument(
        "--bruto",
        action="store_true",
        help="Compara sem normalizar espaços e formatação (comportamento antigo).",
    )
    args = parser.parse_args()

    try:
        precisao, taxa_erro = comparar_textos(args.ocr, args.gabarito, not args.bruto)
    except (FileNotFoundError, ValueError) as e:
        print(f"Erro: {e}")
        return 1

    print(f"CER: {taxa_erro:.4f}")
    print(f"Precisão da comparação: {precisao:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
