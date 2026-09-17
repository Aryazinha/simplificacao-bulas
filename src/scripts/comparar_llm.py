"""Mede o CER de um texto reconstruído por LLM contra o gabarito.

O arquivo e o nome do modelo são passados por argumento, de modo que a linha gravada
em resultados/historico_resultados.txt corresponda de fato ao arquivo medido.

Exemplos:
    python src/comparacao/comparar_llm.py resultados/resultado_claude.txt --modelo Claude
    python src/comparacao/comparar_llm.py resultados/resultado_gemini.txt --modelo Gemini --bruto
"""

import argparse
import datetime
import re
import sys
import unicodedata
from pathlib import Path

from jiwer import cer

RAIZ = Path(__file__).resolve().parents[2]
GABARITO_PADRAO = "dados/gabarito/bula_gabarito.txt"
ARQUIVO_HISTORICO = "resultados/historico_resultados.txt"

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def caminho(valor: str) -> Path:
    """Resolve caminhos relativos a partir da raiz do projeto, não do cwd."""
    p = Path(valor)
    return p if p.is_absolute() else RAIZ / p


def normalizar(texto: str) -> str:
    """Remove formatação Markdown e uniformiza espaços antes da comparação.

    As LLMs devolvem o texto com negrito, títulos e marcadores de lista que o gabarito
    não possui. Sem esta etapa, esses caracteres entram no CER como se fossem erro de
    reconstrução e o ranking entre modelos passa a medir formatação, não fidelidade.
    """
    texto = unicodedata.normalize("NFKC", texto)

    # Blocos e trechos de código: remove as cercas/crases, preserva o conteúdo.
    texto = re.sub(r"```[^\n]*\n", " ", texto)
    texto = texto.replace("```", " ").replace("`", "")

    # Títulos (# ...) e marcadores de lista no início da linha.
    texto = re.sub(r"(?m)^[ \t]*#{1,6}[ \t]*", "", texto)
    texto = re.sub(r"(?m)^[ \t]*(?:[-*+•]|\d+[.)])[ \t]+", "", texto)

    # Negrito/itálico: **texto**, __texto__, *texto*, _texto_.
    texto = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", texto, flags=re.DOTALL)
    texto = re.sub(r"__(.+?)__", r"\1", texto, flags=re.DOTALL)

    # Linhas horizontais (---, ***, ___) e espaços redundantes.
    texto = re.sub(r"(?m)^[ \t]*([-*_])(?:[ \t]*\1){2,}[ \t]*$", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def comparar_textos_llm(
    arquivo_llm: str,
    arquivo_gabarito: str = GABARITO_PADRAO,
    normalizado: bool = True,
) -> tuple[float, float]:
    """Retorna (precisão em %, CER) entre o arquivo informado e o gabarito."""
    caminho_llm = caminho(arquivo_llm)
    caminho_gabarito = caminho(arquivo_gabarito)

    for alvo in (caminho_llm, caminho_gabarito):
        if not alvo.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {alvo}")

    texto_llm = caminho_llm.read_text(encoding="utf-8")
    texto_gabarito = caminho_gabarito.read_text(encoding="utf-8")

    if normalizado:
        texto_llm = normalizar(texto_llm)
        texto_gabarito = normalizar(texto_gabarito)

    if not texto_gabarito:
        raise ValueError(f"Gabarito vazio: {caminho_gabarito}")

    print(f"Gabarito: {len(texto_gabarito)} caracteres")
    print(f"LLM: {len(texto_llm)} caracteres")

    taxa_erro = cer(texto_gabarito, texto_llm)
    precisao = (1 - taxa_erro) * 100

    return precisao, taxa_erro


def registrar_historico(modelo: str, taxa_erro: float, precisao: float, normalizado: bool) -> None:
    momento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    modo = "normalizado" if normalizado else "bruto"
    destino = caminho(ARQUIVO_HISTORICO)
    destino.parent.mkdir(parents=True, exist_ok=True)

    with open(destino, "a", encoding="utf-8") as log:
        log.write(
            f"[{momento}] Modelo: {modelo} | CER: {taxa_erro:.4f} "
            f"| Precisão: {precisao:.2f}% | Texto: {modo}\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "arquivo",
        help="Arquivo com o texto reconstruído pela LLM (ex: resultados/resultado_gemini.txt)",
    )
    parser.add_argument(
        "--modelo",
        help="Nome do modelo gravado no histórico. Padrão: inferido do nome do arquivo.",
    )
    parser.add_argument("--gabarito", default=GABARITO_PADRAO, help="Arquivo de referência.")
    parser.add_argument(
        "--bruto",
        action="store_true",
        help="Compara sem remover a formatação Markdown (comportamento antigo).",
    )
    parser.add_argument("--sem-log", action="store_true", help="Não grava no histórico.")
    args = parser.parse_args()

    modelo = args.modelo or Path(args.arquivo).stem.replace("resultado_", "")
    normalizado = not args.bruto

    try:
        precisao, taxa_erro = comparar_textos_llm(args.arquivo, args.gabarito, normalizado)
    except (FileNotFoundError, ValueError) as e:
        print(f"Erro: {e}")
        return 1

    print(f"Modelo: {modelo}")
    print(f"CER: {taxa_erro:.4f}")
    print(f"Precisão da comparação: {precisao:.2f}%")

    if not args.sem_log:
        registrar_historico(modelo, taxa_erro, precisao, normalizado)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
