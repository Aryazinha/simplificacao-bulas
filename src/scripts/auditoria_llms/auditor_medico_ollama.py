import json
import ollama

def auditar_texto_medico(texto_original: str, texto_simplificado: str, modelo: str = "llama3.2") -> dict:
    """
    Usa o Ollama localmente para atuar como Auditor Médico Independente.
    Avalia se a simplificação do texto manteve a fidelidade clínica.
    """
    
    # Prompt do Sistema definindo o papel rigoroso do Auditor
    system_prompt = """Você é um Auditor Médico sênior, especialista em revisão de Prontuários Eletrônicos (PEP).
Sua missão é comparar um texto médico original com a sua versão simplificada gerada por outra IA.
Você deve avaliar rigorosamente se a versão simplificada:
1. Manteve todos os diagnósticos corretos.
2. Manteve todos os medicamentos e dosagens exatas. É permitido e desejável transformar termos médicos e jargões (como 8/8h) em linguagem comum (a cada 8 horas), desde que o significado clínico temporal não mude.
3. Não introduziu informações falsas ou alucinações (ex: inventar sintomas, diagnósticos ou tratamentos).
4. Manteve o sentido clínico intacto, apenas simplificando a linguagem para o paciente entender.

Retorne APENAS um objeto JSON válido no seguinte formato e absolutamente nada mais (sem explicações adicionais fora do JSON):
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
        # Chama o servidor Ollama rodando localmente na máquina
        # O argumento format="json" garante que o Llama retorne um JSON válido
        response = ollama.chat(
            model=modelo,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            format="json",
            options={
                "temperature": 0.0 # Temperatura baixa para análises mais determinísticas
            }
        )
        
        resultado_str = response['message']['content'].strip()
        return json.loads(resultado_str)
        
    except ollama.ResponseError as e:
        print(f"Erro no Ollama (modelo ausente ou problema no servidor): {e}")
        print(f"Dica: Certifique-se de que rodou 'ollama run {modelo}' no terminal.")
        return None
    except Exception as e:
        print(f"Erro inesperado ao chamar o Ollama: {e}")
        return None


if __name__ == "__main__":
    # EXEMPLO DE USO:
    
    print("Iniciando auditoria médica via Ollama local...")
    print("Nota: A primeira execução pode demorar um pouco dependendo do seu hardware.\n")
    
    # 1. Caso de Falha (Erro na simplificação - Troca de dose)
    original = "O paciente apresentou quadro de cefaleia tensional crônica. Prescrito Paracetamol 750mg de 8/8h."
    simplificado_ruim = "Você tem dor de cabeça constante. Pode tomar Paracetamol 500mg três vezes ao dia."
    
    print("--- TESTE 1: Simplificação Incorreta (Dose Errada) ---")
    resultado = auditar_texto_medico(original, simplificado_ruim)
    if resultado:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    # 2. Caso de Sucesso
    simplificado_bom = "Você apresenta dores de cabeça do tipo tensional. Foi receitado Paracetamol 750mg para tomar a cada 8 horas."
    
    print("\n--- TESTE 2: Simplificação Correta ---")
    resultado2 = auditar_texto_medico(original, simplificado_bom)
    if resultado2:
        print(json.dumps(resultado2, indent=2, ensure_ascii=False))
