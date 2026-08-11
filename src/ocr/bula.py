import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocessar(imagem_cinza, escala=3) -> any:
    """Aplica resize, denoising e binarização adaptativa."""
    redimensionada = cv2.resize(
        imagem_cinza, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC
    )
    denoised = cv2.fastNlMeansDenoising(redimensionada, h=25)
    tratada = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, 10
    )
    return tratada


def ocr_em_bloco(imagem_tratada, psm=4) -> str:

    config = rf'--psm {psm} -l por'
    return pytesseract.image_to_string(imagem_tratada, config=config)


def escanear_bula(caminho_imagem, colunas=2, psm=4, salvar_debug=True) -> str:

    imagem = cv2.imread(caminho_imagem)
    if imagem is None:
        raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")

    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    altura, largura = cinza.shape

    textos = []
    largura_coluna = largura // colunas

    for i in range(colunas):
        x_inicio = i * largura_coluna
        x_fim = largura if i == colunas - 1 else (i + 1) * largura_coluna
        bloco = cinza[:, x_inicio:x_fim]

        bloco_tratado = preprocessar(bloco)

        if salvar_debug:
            cv2.imwrite(f"dados/processadas/bula_tratada_coluna_{i+1}.png", bloco_tratado)

        texto_bloco = ocr_em_bloco(bloco_tratado, psm=psm)
        textos.append(texto_bloco)

    texto_completo = "\n\n".join(textos)
    
    return texto_completo.strip()


if __name__ == "__main__":
    caminho_da_foto = 'dados/entrada/bula_teste.jpeg'

    try:
        print("Iniciando o OCR da bula (sem pós-processamento)...")
        texto = escanear_bula(caminho_da_foto, colunas=2, psm=4)

        print("\n--- TEXTO EXTRAÍDO ---")
        print(texto)

        with open("resultados/bula_extraida.txt", "w", encoding="utf-8") as f:
            f.write(texto)
        print("\nTexto original salvo em 'resultados/bula_extraida.txt'")

    except Exception as e:
        print(f"Erro ao processar: {e}")