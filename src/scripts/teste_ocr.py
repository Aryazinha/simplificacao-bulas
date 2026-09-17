"""Rascunho de OCR direto, sem divisão em colunas nem binarização.

Serve para comparar rapidamente o resultado do Tesseract "cru" com o pipeline de
src/ocr/bula.py. O caminho do executável vem de TESSERACT_CMD (ambiente ou .env).

Exemplos:
    python src/ocr/teste_ocr.py
    python src/ocr/teste_ocr.py --escala 2 --mostrar
"""

import argparse
import os
import sys
from pathlib import Path

import cv2
import numpy as np
import pytesseract

RAIZ = Path(__file__).resolve().parents[2]
IMAGEM_PADRAO = "dados/entrada/bula_teste.jpeg"

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

    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        chave = chave.strip()
        valor = valor.strip().strip('"').strip("'")
        if chave and chave not in os.environ:
            os.environ[chave] = valor


def configurar_tesseract() -> None:
    carregar_env()
    comando = os.environ.get("TESSERACT_CMD", "").strip()

    if comando:
        if not Path(comando).exists():
            raise FileNotFoundError(
                f"TESSERACT_CMD aponta para um arquivo inexistente: {comando}"
            )
        pytesseract.pytesseract.tesseract_cmd = comando


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--imagem", default=IMAGEM_PADRAO, help="Foto da bula.")
    parser.add_argument("--escala", type=float, default=1.0, help="Fator de redimensionamento.")
    parser.add_argument("--psm", type=int, default=6, help="Page segmentation mode.")
    parser.add_argument(
        "--mostrar",
        action="store_true",
        help="Abre uma janela com a imagem (bloqueia até uma tecla ser pressionada).",
    )
    args = parser.parse_args()

    try:
        configurar_tesseract()
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        return 1

    # cv2.imread falha com caracteres não-ASCII no caminho (Windows), por isso o
    # arquivo é lido pelo Python e decodificado em memória.
    arquivo = caminho(args.imagem)
    dados = np.fromfile(str(arquivo), dtype=np.uint8) if arquivo.exists() else np.array([])
    imagem_cinza = (
        cv2.imdecode(dados, cv2.IMREAD_GRAYSCALE) if dados.size else None
    )
    if imagem_cinza is None:
        print(f"Erro: imagem não encontrada ou ilegível: {arquivo}")
        return 1

    if args.escala != 1.0:
        imagem_cinza = cv2.resize(
            imagem_cinza, None, fx=args.escala, fy=args.escala, interpolation=cv2.INTER_LINEAR
        )

    try:
        texto_extraido = pytesseract.image_to_string(
            imagem_cinza, config=rf"--oem 3 --psm {args.psm} -l por"
        )
    except pytesseract.TesseractNotFoundError:
        print(
            "Erro: Tesseract não encontrado. Instale-o e, se não estiver no PATH, "
            "defina TESSERACT_CMD no .env."
        )
        return 1

    print("--- TEXTO EXTRAÍDO ---")
    print(texto_extraido.strip())

    if args.mostrar:
        cv2.imshow("Imagem", imagem_cinza)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
