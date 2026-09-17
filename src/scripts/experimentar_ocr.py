"""Script de linha de comando para testar a extração OCR (Herdado da Fase 1).

Exemplos:
    python src/scripts/experimentar_ocr.py
    python src/scripts/experimentar_ocr.py --imagem dados/entrada/outra_bula.jpeg --colunas 3
"""

import argparse
import sys
from pathlib import Path
import easyocr

# Garante que imports absolutos a partir de 'src' funcionem
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.core.ocr.scanner import escanear_bula

RAIZ = Path(__file__).resolve().parents[2]
IMAGEM_PADRAO = "dados/entrada/bula_teste.jpeg"
SAIDA_PADRAO = "resultados/bula_extraida.txt"
PASTA_DEBUG = "dados/processadas"

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

def caminho(*partes: str) -> Path:
    p = Path(*partes)
    return p if p.is_absolute() else RAIZ / p

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--imagem", default=IMAGEM_PADRAO, help="Foto da bula.")
    parser.add_argument("--saida", default=SAIDA_PADRAO, help="Arquivo de saída do texto.")
    parser.add_argument("--colunas", type=int, default=2, help="Faixas verticais da imagem.")
    parser.add_argument(
        "--psm", 
        type=int, 
        default=4, 
        help="Mantido por retrocompatibilidade (ignorado pelo EasyOCR)."
    )
    parser.add_argument(
        "--sem-debug",
        action="store_true",
        help=f"Não salva as imagens pré-processadas em {PASTA_DEBUG}/.",
    )
    args = parser.parse_args()

    try:
        print("Inicializando o EasyOCR...")
        reader = easyocr.Reader(['pt'])

        print("Iniciando o OCR da bula (sem pós-processamento)...")
        # Ajustar caminho da imagem para absoluto caso seja relativo
        arq_imagem = caminho(args.imagem)
        
        texto = escanear_bula(
            str(arq_imagem),
            colunas=args.colunas,
            salvar_debug=not args.sem_debug,
            reader=reader
        )

        print("\n--- TEXTO EXTRAÍDO ---")
        print(texto)

        destino = caminho(args.saida)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
        print(f"\nTexto original salvo em '{destino}'")

    except Exception as e:
        print(f"Erro ao processar: {e}")
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
