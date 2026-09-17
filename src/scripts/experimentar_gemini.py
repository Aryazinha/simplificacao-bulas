"""Reconstrói, via Gemini, o texto de bula extraído pelo OCR (CLI de experimentação).

Exemplos:
    python src/scripts/experimentar_gemini.py
"""

import argparse
import os
import sys
from pathlib import Path

# Garante que imports absolutos a partir de 'src' funcionem
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.core.llm.gemini_client import reconstruir_bula_com_gemini, MODELO_PADRAO, ENTRADA_PADRAO, SAIDA_PADRAO, carregar_env

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> int:
    carregar_env()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--modelo",
        default=os.environ.get("GEMINI_MODEL_GERADOR", MODELO_PADRAO),
        help=f"ID do modelo Gemini. Padrão: {MODELO_PADRAO} (ou GEMINI_MODEL_GERADOR).",
    )
    parser.add_argument("--entrada", default=ENTRADA_PADRAO, help="Texto extraído pelo OCR.")
    parser.add_argument("--saida", default=SAIDA_PADRAO, help="Arquivo de saída (JSON).")
    args = parser.parse_args()

    resultado = reconstruir_bula_com_gemini(args.modelo, args.entrada, args.saida)

    if not resultado:
        return 1

    print("\n===== BULA SIMPLIFICADA E ESTRUTURADA (JSON) =====\n")
    print(resultado)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
