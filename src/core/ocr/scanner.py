"""Extrai o texto de uma foto de bula com pré-processamento OpenCV + EasyOCR.

Exemplos:
    python src/ocr/bula.py
    python src/ocr/bula.py --imagem dados/entrada/outra_bula.jpeg --colunas 3
"""

import os
from pathlib import Path

# cv2 (OpenCV) é usado para manipulação avançada de imagens (redimensionamento, conversão de cores).
import cv2
# easyocr é a biblioteca de Optical Character Recognition baseada em Deep Learning.
import easyocr
# numpy lida com arrays numéricos, formato que o OpenCV utiliza internamente para representar imagens.
import numpy as np

RAIZ = Path(__file__).resolve().parents[2]



def caminho(*partes: str) -> Path:
    """Resolve caminhos relativos a partir da raiz do projeto, não do cwd (Current Working Directory)."""
    p = Path(*partes)
    return p if p.is_absolute() else RAIZ / p


def ler_imagem(arquivo: Path, flags=cv2.IMREAD_COLOR):
    """Lê a imagem via buffer.

    cv2.imread falha silenciosamente quando o caminho contém caracteres não-ASCII no
    Windows (o projeto fica em ".../Área de Trabalho/..."), então o arquivo é lido pelo
    Python nativo (`np.fromfile`) e decodificado em memória via `cv2.imdecode`.
    """
    if not arquivo.exists():
        return None

    # Lê o arquivo binário direto para um array NumPy
    dados = np.fromfile(str(arquivo), dtype=np.uint8)
    if dados.size == 0:
        return None

    # Decodifica o array binário para o formato de matriz de imagem BGR do OpenCV
    return cv2.imdecode(dados, flags)


def salvar_imagem(arquivo: Path, imagem) -> bool:
    """Grava a imagem via buffer, pelo mesmo motivo de `ler_imagem`."""
    # imencode converte a matriz OpenCV de volta para bytes (png/jpg)
    ok, buffer = cv2.imencode(arquivo.suffix or ".png", imagem)
    if not ok:
        return False

    # tofile escreve os bytes no disco suportando caminhos complexos do Windows
    buffer.tofile(str(arquivo))
    return True


def preprocessar(imagem_cinza, escala=3):
    """Aplica resize para facilitar a leitura.
    
    A remoção de ruído e binarização foram retiradas pois o EasyOCR
    (baseado em redes neurais) performa melhor com bordas suaves (Grayscale original).
    """
    # INTER_CUBIC é uma técnica de interpolação matemática que mantém as bordas das letras mais nítidas ao ampliar
    redimensionada = cv2.resize(
        imagem_cinza, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC
    )
    return redimensionada


def ocr_em_bloco(reader: easyocr.Reader, imagem_tratada) -> str:
    # `detail=0` diz ao EasyOCR para retornar apenas os textos crus, 
    # ignorando as coordenadas (bounding boxes) e a confiança (confidence score).
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

    # cvtColor converte a imagem colorida (BGR) para tons de cinza (Grayscale),
    # o que reduz a complexidade (de 3 canais de cor para 1 canal) e acelera o processamento do OCR.
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    largura = cinza.shape[1] # shape[1] é a largura em pixels. shape[0] seria a altura.

    if colunas > largura:
        raise ValueError(f"Colunas ({colunas}) excede a largura da imagem ({largura}px).")

    if salvar_debug:
        caminho(PASTA_DEBUG).mkdir(parents=True, exist_ok=True)

    textos = []
    largura_coluna = largura // colunas
    
    # Inicializa o reader caso não tenha sido passado externamente (útil para uso em CLI)
    if reader is None:
        print("Inicializando o modelo do EasyOCR (pode demorar na primeira vez)...")
        reader = easyocr.Reader(['pt'])

    # Fatiamos a imagem verticalmente (Crop) utilizando Numpy Slicing: `cinza[:, x_inicio:x_fim]`
    for i in range(colunas):
        x_inicio = i * largura_coluna
        x_fim = largura if i == colunas - 1 else (i + 1) * largura_coluna
        
        # Slicing: Pega todas as linhas (:), mas restringe as colunas entre x_inicio e x_fim
        bloco = cinza[:, x_inicio:x_fim]

        bloco_tratado = preprocessar(bloco)

        if salvar_debug:
            destino_debug = caminho(PASTA_DEBUG, f"bula_tratada_coluna_{i + 1}.png")
            salvar_imagem(destino_debug, bloco_tratado)

        texto_bloco = ocr_em_bloco(reader, bloco_tratado)
        if texto_bloco:
            textos.append(texto_bloco)

    # Une os blocos extraídos separados por duas quebras de linha para manter a hierarquia
    return "\n\n".join(textos).strip()

