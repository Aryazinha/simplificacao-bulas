import os
import json
from google import genai
from google.genai import types

# Tente importar o load_dotenv, se a biblioteca python-dotenv estiver instalada
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def auditar_texto_medico(texto_original: str, texto_simplificado: str, modelo: str = None) -> dict:
    """
    Usa a API do Gemini para atuar como Auditor Médico Independente.
    Avalia se a simplificação do texto manteve a fidelidade clínica.
    """
    if modelo is None:
        modelo = os.getenv("GEMINI_MODEL_AUDITOR", "gemini-3.6-flash")

    
    # Inicializa o cliente do Gemini. Ele pega automaticamente a chave GEMINI_API_KEY do ambiente.
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GEMINI_API_KEY não foi encontrada. Verifique seu arquivo .env")
        
    client = genai.Client(api_key=api_key)
    
    # Prompt do Sistema definindo o papel rigoroso do Auditor
    system_prompt = """Você é um Auditor Médico sênior, especialista em revisão de Prontuários Eletrônicos (PEP).
Sua missão é comparar um texto médico original com a sua versão simplificada gerada por outra IA.
Você deve avaliar rigorosamente se a versão simplificada:
1. Manteve todos os diagnósticos corretos.
2. Manteve todos os medicamentos e dosagens exatas. É permitido e desejável transformar termos médicos e jargões (como 8/8h) em linguagem comum (a cada 8 horas), desde que o significado clínico temporal não mude.
3. Não introduziu informações falsas ou alucinações (ex: inventar sintomas, diagnósticos ou tratamentos).
4. Manteve o sentido clínico intacto, apenas simplificando a linguagem para o paciente entender.

Retorne APENAS um JSON válido no seguinte formato e nada mais (não adicione blocos de markdown ```json):
{
    "diagnosticos_mantidos": true/false,
    "medicamentos_e_doses_exatos": true/false,
    "sem_alucinacoes": true/false,
    "aprovado": true/false,
    "justificativa": "Sua explicação clínica detalhada e objetiva sobre a decisão (se reprovado, liste o erro)."
}"""

    # Prompt do Usuário enviando os textos
    user_prompt = f"""TEXTO MÉDICO ORIGINAL:
{texto_original}

TEXTO SIMPLIFICADO PELA IA:
{texto_simplificado}

Analise a fidelidade e gere o JSON."""

    try:
        response = client.models.generate_content(
            model=modelo,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        
        # Limpa o resultado caso o modelo ainda coloque markdown de formatação
        resultado_str = response.text.strip()
        if resultado_str.startswith("```json"):
            resultado_str = resultado_str.replace("```json", "").replace("```", "").strip()
            
        return json.loads(resultado_str)
        
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return None


if __name__ == "__main__":
    # EXEMPLO DE USO:
    
    # 1. Caso de Falha (Erro na simplificação - Troca de dose)
    original = "O paciente apresentou quadro de cefaleia tensional crônica. Prescrito Paracetamol 750mg de 8/8h."
    simplificado_ruim = "Você tem dor de cabeça constante. Pode tomar Paracetamol 500mg três vezes ao dia."
    
    print("--- TESTE 1: Simplificação Incorreta (Dose Errada) ---")
    resultado = auditar_texto_medico(original, simplificado_ruim)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    # 2. Caso de Sucesso
    simplificado_bom = "Você apresenta dores de cabeça do tipo tensional. Foi receitado Paracetamol 750mg para tomar a cada 8 horas."
    
    print("\n--- TESTE 2: Simplificação Correta ---")
    resultado2 = auditar_texto_medico(original, simplificado_bom)
    print(json.dumps(resultado2, indent=2, ensure_ascii=False))
