import argparse
import sys
import json
from pathlib import Path

# Adiciona o raiz para import
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.comparacao.fidelidade import EmbeddingService, chunk_text, auditar_secao, cosine_similarity

RAIZ = Path(__file__).resolve().parents[2]

CHAVES_ESPERADAS = {
    "indicacao", "funcionamento", "contraindicacoes", "precaucoes_populacoes_especiais",
    "interacoes_medicamentosas", "armazenamento", "posologia_uso", "esquecimento",
    "efeitos_colaterais", "superdose", "avisos_seguranca"
}

def principal():
    parser = argparse.ArgumentParser(description="Avalia fidelidade factual e semântica das seções.")
    parser.add_argument("--original", required=True, help="Bula original.")
    parser.add_argument("--simplificado", required=True, help="Bula simplificada (JSON).")
    # Usa llama3.2 por padrão como verificador independente, impedindo viés de quem gerou (Gemini)
    parser.add_argument("--modelo-auditor", default="llama3.2", help="Modelo Ollama para auditoria.")
    args = parser.parse_args()

    caminho_orig = RAIZ / args.original
    caminho_simp = RAIZ / args.simplificado
    caminho_prompt = RAIZ / "src" / "comparacao" / "prompt_verificador.txt"
    
    if not caminho_orig.exists():
        print(f"Erro: Arquivo original não encontrado: {caminho_orig}")
        return 1
    if not caminho_simp.exists():
        print(f"Erro: Arquivo simplificado não encontrado: {caminho_simp}")
        return 1
    if not caminho_prompt.exists():
        print(f"Erro: Prompt de validação não encontrado: {caminho_prompt}")
        return 1
        
    texto_orig = caminho_orig.read_text(encoding='utf-8').strip()
    texto_simp_bruto = caminho_simp.read_text(encoding='utf-8').strip()
    prompt_template = caminho_prompt.read_text(encoding='utf-8')
    
    try:
        dados_simp = json.loads(texto_simp_bruto)
    except json.JSONDecodeError:
        print("Erro: O arquivo simplificado não é um JSON estruturado válido. Necessário output gerado no Passo 1.2.")
        return 1

    chaves_presentes = set(dados_simp.keys())
    chaves_faltantes = CHAVES_ESPERADAS - chaves_presentes
    
    if chaves_faltantes:
        print(f"Aviso: As seguintes seções estão faltando no JSON e não serão avaliadas: {chaves_faltantes}\n")

    print("Iniciando serviço de Embeddings (verificando chaves e limites)...")
    try:
        embedder = EmbeddingService()
    except ImportError as e:
        print(f"Erro Fatal: {e}")
        return 1
        
    backend_usado = "Local (sentence-transformers)" if embedder.use_local else "API (gemini-embedding-001)"
    print(f"Backend de Embedding ativo: {backend_usado}\n")
    
    print("Processando chunks do texto original para bypass no limite de tokens...")
    chunks_orig = chunk_text(texto_orig, max_words=150)
    emb_origs = [embedder.get_embedding(c) for c in chunks_orig if c.strip()]
    
    resultados_secoes = {}
    
    print("\n--- AVALIAÇÃO DE FIDELIDADE (SEÇÃO A SEÇÃO) ---")
    for secao, texto_secao in dados_simp.items():
        if not texto_secao or str(texto_secao).startswith("Não há essa informação"):
            continue
            
        print(f"\nAvaliando: [{secao}]")
        
        # Avaliação de Cosseno
        emb_secao = embedder.get_embedding(str(texto_secao))
        similaridades = [cosine_similarity(emb_secao, eo) for eo in emb_origs if eo]
        max_sim = max(similaridades) if similaridades else 0.0
        
        # Avaliação Factual LLM Cruzado
        auditoria = auditar_secao(secao, str(texto_secao), texto_orig, prompt_template, args.modelo_auditor)
        
        resultados_secoes[secao] = {
            "cosseno_maximo": round(max_sim, 4),
            "veredito_factual": auditoria["veredito_factual"],
            "divergencias": auditoria["divergencias_encontradas"]
        }
        
        print(f"  - Similaridade Máxima (Cosseno): {max_sim:.4f}")
        print(f"  - Veredito Factual: {auditoria['veredito_factual']}")
        if auditoria['divergencias_encontradas']:
            print("  - Divergências:")
            for d in auditoria['divergencias_encontradas']:
                print(f"      - {d}")

    # Salvar resultados
    pasta_saida = RAIZ / "resultados" / "avaliacoes"
    pasta_saida.mkdir(parents=True, exist_ok=True)
    
    arquivo_saida = pasta_saida / "metricas_fidelidade.json"
    arquivo_saida.write_text(json.dumps(resultados_secoes, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nResultados exportados para: {arquivo_saida}")
    
    return 0

if __name__ == "__main__":
    sys.exit(principal())
