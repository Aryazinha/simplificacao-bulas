from jiwer import cer
import sys
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def comparar_textos() -> tuple[float, float]:
    arquivo_ocr = "resultados/bula_extraida.txt"
    arquivo_gabarito = "dados/gabarito/bula_gabarito.txt"

    with open(arquivo_ocr, "r", encoding="utf-8") as f:
        texto_ocr = f.read()
    with open(arquivo_gabarito, "r", encoding="utf-8") as f:
        texto_gabarito = f.read()
    
    print(f"Gabarito: {len(texto_gabarito)} caracteres")
    print(f"OCR: {len(texto_ocr)} caracteres")

    taxa_erro = cer(texto_gabarito, texto_ocr)

    precisao = (1 - taxa_erro) * 100

    return precisao, taxa_erro

if __name__ == "__main__":
    precisao, taxa_erro = comparar_textos()
    print(f"CER: {taxa_erro:.4f}")
    print(f"Precisão da comparação: {precisao:.2f}%")
