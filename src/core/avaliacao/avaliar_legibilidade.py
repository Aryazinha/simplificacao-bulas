import argparse
import sys
import json
from pathlib import Path

# Adiciona o raiz para import
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.comparacao.legibilidade import calcular_metricas, carregar_termos_tecnicos

RAIZ = Path(__file__).resolve().parents[2]

def principal():
    parser = argparse.ArgumentParser(description="Avalia métricas de legibilidade de bulas.")
    parser.add_argument("--original", required=True, help="Caminho para a bula extraída pelo OCR.")
    parser.add_argument("--simplificado", required=True, help="Caminho para a bula simplificada pelo LLM.")
    args = parser.parse_args()

    caminho_orig = RAIZ / args.original
    caminho_simp = RAIZ / args.simplificado
    caminho_termos = RAIZ / "src" / "comparacao" / "termos_tecnicos.txt"
    
    if not caminho_orig.exists():
        print(f"Erro: Arquivo original não encontrado em {caminho_orig}")
        return 1
    if not caminho_simp.exists():
        print(f"Erro: Arquivo simplificado não encontrado em {caminho_simp}")
        return 1
        
    texto_orig = caminho_orig.read_text(encoding='utf-8').strip()
    texto_simp = caminho_simp.read_text(encoding='utf-8').strip()
    
    if not texto_orig:
        print("Erro: O arquivo original está vazio.")
        return 1
    if not texto_simp:
        print("Erro: O arquivo simplificado está vazio.")
        return 1
        
    termos_tecnicos = carregar_termos_tecnicos(caminho_termos)
    
    try:
        metricas_orig = calcular_metricas(texto_orig, termos_tecnicos)
    except ValueError as e:
        print(f"Processamento abortado. Arquivo original falhou: {e}")
        return 1
        
    try:
        # Tenta extrair apenas valores textuais caso o simplificado seja um JSON (estruturado do Passo 1.2)
        try:
            dados_json = json.loads(texto_simp)
            texto_simp_puro = " ".join(str(v) for v in dados_json.values())
        except json.JSONDecodeError:
            texto_simp_puro = texto_simp
            
        metricas_simp = calcular_metricas(texto_simp_puro, termos_tecnicos)
    except ValueError as e:
        print(f"Processamento abortado. Arquivo simplificado falhou: {e}")
        return 1
        
    print("\n--- AVALIAÇÃO DE LEGIBILIDADE E COMPLEXIDADE ---")
    print(f"{'Métrica':<35} | {'Original':<10} | {'Simplificado':<15} | {'Ganho/Variação'}")
    print("-" * 80)
    
    ganho_flesch = metricas_simp['flesch_index'] - metricas_orig['flesch_index']
    print(f"{'Índice Flesch (PT-BR)':<35} | {metricas_orig['flesch_index']:<10} | {metricas_simp['flesch_index']:<15} | {ganho_flesch:+.2f}")
    
    var_frase = metricas_simp['comprimento_medio_frase'] - metricas_orig['comprimento_medio_frase']
    print(f"{'Comprimento Médio da Frase':<35} | {metricas_orig['comprimento_medio_frase']:<10} | {metricas_simp['comprimento_medio_frase']:<15} | {var_frase:+.2f} pal.")
    
    var_complex = metricas_simp['percentual_palavras_complexas'] - metricas_orig['percentual_palavras_complexas']
    print(f"{'% Palavras Complexas (>3 síl.)':<35} | {metricas_orig['percentual_palavras_complexas']:<10}%| {metricas_simp['percentual_palavras_complexas']:<15}%| {var_complex:+.2f}%")
    
    var_jargao = metricas_simp['densidade_jargao_medico'] - metricas_orig['densidade_jargao_medico']
    print(f"{'Densidade de Jargão Médico':<35} | {metricas_orig['densidade_jargao_medico']:<10}%| {metricas_simp['densidade_jargao_medico']:<15}%| {var_jargao:+.2f}%")
    
    # Salvar resultados
    pasta_saida = RAIZ / "resultados" / "avaliacoes"
    pasta_saida.mkdir(parents=True, exist_ok=True)
    
    resultado_saida = {
        "original": metricas_orig,
        "simplificado": metricas_simp,
        "variacoes": {
            "flesch": ganho_flesch,
            "comprimento_frase": var_frase,
            "palavras_complexas": var_complex,
            "jargao": var_jargao
        }
    }
    
    arquivo_saida = pasta_saida / "metricas_legibilidade.json"
    arquivo_saida.write_text(json.dumps(resultado_saida, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nMétricas detalhadas exportadas para: {arquivo_saida}")
    
    return 0

if __name__ == "__main__":
    sys.exit(principal())
