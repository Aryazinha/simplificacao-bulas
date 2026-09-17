import re
from pathlib import Path

def carregar_termos_tecnicos(caminho_arquivo: Path) -> set:
    if not caminho_arquivo.exists():
        return set()
    linhas = caminho_arquivo.read_text(encoding='utf-8').splitlines()
    return {linha.strip().lower() for linha in linhas if linha.strip()}

def contar_silabas_pt(palavra: str) -> int:
    """Heurística simples para contar sílabas em português baseada em grupos de vogais."""
    palavra = palavra.lower()
    # Remove pontuação
    palavra = re.sub(r'[^a-záéíóúâêôãõüç]', '', palavra)
    if not palavra:
        return 0
    # Encontra grupos de vogais contíguas
    vogais = re.findall(r'[aáàãâeéèêiíìoóòõôuúùü]+', palavra)
    num_silabas = len(vogais)
    return max(1, num_silabas)

def normalizar_texto(texto: str) -> str:
    """Remove quebras de linha excessivas e ruídos típicos de OCR."""
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'([a-z])- ([a-z])', r'\1\2', texto)  # Arruma hifenização de OCR
    return texto.strip()

def calcular_metricas(texto: str, termos_tecnicos: set) -> dict:
    texto_norm = normalizar_texto(texto)
    
    # Dividir em frases (considera . ! ? seguidos de espaço e maiúscula, ou fim do texto)
    frases_sujas = re.split(r'[.!?]+(?:\s+|$)', texto_norm)
    frases = [f.strip() for f in frases_sujas if len(f.strip()) > 3]
    
    if len(frases) < 2:
        raise ValueError("O texto possui menos de duas frases detectáveis após a normalização.")
        
    total_frases = len(frases)
    
    # Dividir em palavras
    palavras_sujas = re.findall(r'\b[a-zA-ZáéíóúâêôãõüçÁÉÍÓÚÂÊÔÃÕÜÇ]+\b', texto_norm)
    palavras = [p for p in palavras_sujas if p]
    total_palavras = len(palavras)
    
    if total_palavras == 0:
        raise ValueError("O texto não possui palavras válidas.")

    total_silabas = 0
    palavras_mais_tres_silabas = 0
    jargoes_encontrados = 0
    
    for p in palavras:
        silabas = contar_silabas_pt(p)
        total_silabas += silabas
        if silabas > 3:
            palavras_mais_tres_silabas += 1
            
        if p.lower() in termos_tecnicos:
            jargoes_encontrados += 1
            
    # Fórmula de Martins et al. (1996) para o Flesch em Português
    # Flesch = 248.835 - (1.015 * (total_palavras / total_frases)) - (84.6 * (total_silabas / total_palavras))
    asl = total_palavras / total_frases
    asw = total_silabas / total_palavras
    
    flesch = 248.835 - (1.015 * asl) - (84.6 * asw)
    
    return {
        "flesch_index": round(flesch, 2),
        "comprimento_medio_frase": round(asl, 2),
        "percentual_palavras_complexas": round((palavras_mais_tres_silabas / total_palavras) * 100, 2),
        "densidade_jargao_medico": round((jargoes_encontrados / total_palavras) * 100, 2)
    }
