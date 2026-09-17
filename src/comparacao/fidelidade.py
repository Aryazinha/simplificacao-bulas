import os
import json
import numpy as np
from typing import List, Dict
from numpy.linalg import norm
import re
from pathlib import Path

import ollama
from google import genai

RAIZ = Path(__file__).resolve().parents[2]

def carregar_env():
    arquivo = RAIZ / ".env"
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha: continue
        chave, _, valor = linha.partition("=")
        chave = chave.strip()
        if chave and chave not in os.environ:
            os.environ[chave] = valor.strip().strip('"').strip("'")

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if norm(v1) == 0 or norm(v2) == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm(v1) * norm(v2)))

class EmbeddingService:
    def __init__(self):
        carregar_env()
        self.use_local = False
        self.local_model = None
        self.client = None
        
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                # Teste rápido para validar chave e modelo
                self.client.models.embed_content(model="models/embedding-001", contents="teste")
            except Exception as e:
                print(f"\nAviso: Falha na API Gemini ({e}). Fazendo fallback para backend local.")
                self.use_local = True
        else:
            print("\nAviso: GEMINI_API_KEY não encontrada. Fazendo fallback para backend local.")
            self.use_local = True
            
        if self.use_local:
            self._init_local_model()

    def _init_local_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            if not self.local_model:
                self.local_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except ImportError:
            raise ImportError("O backend local requer a biblioteca 'sentence-transformers'. Adicione ao requirements.txt e instale.")

    def get_embedding(self, texto: str) -> List[float]:
        if not texto.strip():
            return []
        
        if self.use_local:
            return self.local_model.encode(texto).tolist()
        else:
            try:
                resp = self.client.models.embed_content(
                    model="models/embedding-001", 
                    contents=texto
                )
                return resp.embeddings[0].values
            except Exception as e:
                if not self.use_local:
                    print(f"\nErro em tempo de execução no Gemini ({e}). Migrando para fallback local.")
                    self.use_local = True
                    self._init_local_model()
                return self.local_model.encode(texto).tolist()

def chunk_text(text: str, max_words=150) -> List[str]:
    """Divide o texto em chunks menores para evitar o limite de 2048 tokens de embeddings antigos."""
    words = text.split()
    return [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

def auditar_secao(nome_secao: str, texto_simp: str, texto_orig: str, prompt_template: str, modelo_ollama="llama3.2") -> Dict:
    prompt = prompt_template.format(
        nome_secao=nome_secao,
        texto_simplificado=texto_simp,
        texto_original=texto_orig
    )
    
    try:
        resposta = ollama.chat(
            model=modelo_ollama,
            messages=[{"role": "user", "content": prompt}],
            format="json",
            options={"temperature": 0.0}
        )
        texto_resp = resposta["message"]["content"].strip()
        
        # Tenta extrair json se o Ollama retornou com blocos markdown
        match = re.search(r'```json\s*(.*?)\s*```', texto_resp, re.DOTALL)
        if match:
            texto_resp = match.group(1)
            
        dados = json.loads(texto_resp)
        return {
            "veredito_factual": dados.get("veredito_factual", "Desconhecido"),
            "divergencias_encontradas": dados.get("divergencias_encontradas", [])
        }
    except Exception as e:
        return {
            "veredito_factual": "Erro de Validação",
            "divergencias_encontradas": [f"Falha ao rodar LLM de validação: {e}"]
        }
