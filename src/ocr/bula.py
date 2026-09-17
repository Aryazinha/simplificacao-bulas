"""Extrai o texto de uma foto de bula com pré-processamento OpenCV + EasyOCR.

Exemplos:
    python src/ocr/bula.py
    python src/ocr/bula.py --imagem dados/entrada/outra_bula.jpeg --colunas 3
"""

import argparse
import os
import sys
from pathlib import Path

import cv2
import easyocr
import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
IMAGEM_PADRAO = "dados/entrada/bula_teste.jpeg"
SAIDA_PADRAO = "resultados/bula_extraida.txt"
PASTA_DEBUG = "dados/processadas"

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def caminho(*partes: str) -> Path:
    """Resolve caminhos relativos a partir da raiz do projeto, não do cwd."""
    p = Path(*partes)
    return p if p.is_absolute() else RAIZ / p


def ler_imagem(arquivo: Path, flags=cv2.IMREAD_COLOR):
    """Lê a imagem via buffer.

    cv2.imread falha silenciosamente quando o caminho contém caracteres não-ASCII no
    Windows (o projeto fica em ".../Área de Trabalho/..."), então o arquivo é lido pelo
    Python e decodificado em memória.
    """
    if not arquivo.exists():
        return None

    dados = np.fromfile(str(arquivo), dtype=np.uint8)
    if dados.size == 0:
        return None

    return cv2.imdecode(dados, flags)


def salvar_imagem(arquivo: Path, imagem) -> bool:
    """Grava a imagem via buffer, pelo mesmo motivo de `ler_imagem`."""
    ok, buffer = cv2.imencode(arquivo.suffix or ".png", imagem)
    if not ok:
        return False

    buffer.tofile(str(arquivo))
    return True


def preprocessar(imagem_cinza, escala=3):
    """Aplica resize para facilitar a leitura.
    
    A remoção de ruído e binarização foram retiradas pois o EasyOCR
    (baseado em redes neurais) performa melhor com bordas suaves.
    """
    redimensionada = cv2.resize(
        imagem_cinza, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC
    )
    return redimensionada


def ocr_em_bloco(reader: easyocr.Reader, imagem_tratada) -> str:
    # `detail=0` retorna apenas a lista de textos detectados
    resultados = reader.readtext(imagem_tratada, detail=0)
    return "\n".join(resultados)


def escanear_bula(caminho_imagem, colunas=2, salvar_debug=True, reader=None) -> str:
    """Divide a imagem em `colunas` faixas verticais e roda o OCR em cada uma."""
    if colunas < 1:
        raise ValueError("O número de colunas deve ser pelo menos 1.")

    arquivo = caminho(caminho_imagem)
    imagem = ler_imagem(arquivo)
    if imagem is None:
        raise FileNotFoundError(f"Imagem não encontrada ou ilegível: {arquivo}")

    # EasyOCR lida bem com BGR/RGB e Grayscale, manteremos cinza para uniformizar o resize e simplificar debug
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    largura = cinza.shape[1]

    if colunas > largura:
        raise ValueError(f"Colunas ({colunas}) excede a largura da imagem ({largura}px).")

    if salvar_debug:
        caminho(PASTA_DEBUG).mkdir(parents=True, exist_ok=True)

    textos = []
    largura_coluna = largura // colunas
    
    # Inicializa o reader caso não tenha sido passado externamente
    if reader is None:
        print("Inicializando o modelo do EasyOCR (pode demorar na primeira vez)...")
        reader = easyocr.Reader(['pt'])

    for i in range(colunas):
        x_inicio = i * largura_coluna
        x_fim = largura if i == colunas - 1 else (i + 1) * largura_coluna
        bloco = cinza[:, x_inicio:x_fim]

        bloco_tratado = preprocessar(bloco)

        if salvar_debug:
            destino_debug = caminho(PASTA_DEBUG, f"bula_tratada_coluna_{i + 1}.png")
            salvar_imagem(destino_debug, bloco_tratado)

        texto_bloco = ocr_em_bloco(reader, bloco_tratado)
        if texto_bloco:
            textos.append(texto_bloco)

    return "\n\n".join(textos).strip()


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
        # Instancia o reader uma vez na main para reutilizar entre as colunas
        reader = easyocr.Reader(['pt'])

        print("Iniciando o OCR da bula (sem pós-processamento)...")
        texto = escanear_bula(
            args.imagem,
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
