from jiwer import cer
import sys
import os
import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def comparar_textos_llm() -> tuple[float, float]:
    arquivo_llm = "resultados/resultado_claude.txt"
    arquivo_gabarito = "dados/gabarito/bula_gabarito.txt"

    with open(arquivo_llm, "r", encoding="utf-8") as f:
        texto_llm = f.read()
    with open(arquivo_gabarito, "r", encoding="utf-8") as f:
        texto_gabarito = f.read()
    
    print(f"Gabarito: {len(texto_gabarito)} caracteres")
    print(f"LLM: {len(texto_llm)} caracteres")

    taxa_erro = cer(texto_gabarito, texto_llm)

    precisao = (1 - taxa_erro) * 100

    return precisao, taxa_erro

if __name__ == "__main__":
    precisao, taxa_erro = comparar_textos_llm()
    print(f"CER: {taxa_erro:.4f}")
    print(f"Precisão da comparação: {precisao:.2f}%")

    times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("resultados/historico_resultados.txt", "a", encoding="utf-8") as log:
        log.write(f"[{times}] Modelo: Claude | CER: {taxa_erro:.4f} | Precisão: {precisao:.2f}%\n")