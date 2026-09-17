import json
from pydantic import BaseModel, Field

# Schema Pydantic opcional (útil para uso no Gemini SDK recente)
class BulaSimplificada(BaseModel):
    indicacao: str = Field(description="1. Para que este medicamento é indicado?")
    funcionamento: str = Field(description="2. Como este medicamento funciona?")
    contraindicacoes: str = Field(description="3. Quando não devo usar este medicamento?")
    precaucoes_populacoes_especiais: str = Field(description="Avisos específicos para gestantes, lactantes, idosos, crianças e doenças prévias.")
    interacoes_medicamentosas: str = Field(description="O que saber antes de usar (interação com alimentos, álcool e outros remédios).")
    armazenamento: str = Field(description="4. Onde, como e por quanto tempo posso guardar este medicamento?")
    posologia_uso: str = Field(description="5. Como devo usar este medicamento? (Converta tabelas em listas legíveis).")
    esquecimento: str = Field(description="6. O que devo fazer quando eu me esquecer de usar este medicamento?")
    efeitos_colaterais: str = Field(description="7. Quais os males que este medicamento pode me causar?")
    superdose: str = Field(description="8. O que fazer se alguém usar uma quantidade maior do que a indicada?")
    avisos_seguranca: str = Field(description="Alertas obrigatórios (ex: 'Não se automedique', 'Converse com seu médico').")


PROMPT_SISTEMA_BULA = """Você é um especialista médico focado em comunicação clara e acessível em saúde para pacientes leigos.
Sua tarefa é ler um texto extraído por OCR de uma bula de medicamento e simplificá-lo de forma segura e estruturada, 
atendendo às diretrizes da ANVISA (RDC nº 47/2009 da Bula do Paciente).

REGRAS CRÍTICAS DE SEGURANÇA E ROBUSTEZ:
1. NUNCA perca precisão em: Contraindicações, Dose Máxima, Interações Medicamentosas Graves e Sinais de Reações Alérgicas.
2. NUNCA suavize alertas obrigatórios (ex: "não se automedique", "converse com seu médico").
3. Múltiplos Princípios Ativos: Se a bula contiver mais de um princípio ativo, deixe absolutamente claro a qual deles o efeito ou interação se refere.
4. Tabelas: Converta tabelas de posologia ou interações contidas no OCR em listas claras e fáceis de ler.
5. Populações Especiais: Agrupe orientações sobre Gestantes, Lactantes, Idosos, Crianças e Doenças Prévias no seu campo correspondente.
6. Fallback (Informação Ausente): Se a bula não trouxer a resposta para alguma das perguntas, preencha o campo EXATAMENTE com: "Não há essa informação na bula original." (Proibido inferir, adivinhar ou alucinar dados).
7. Trechos Ilegíveis: Se o texto original estiver corrompido ou ilegível a ponto de prejudicar o entendimento exato daquela seção, adicione "[Atenção: Trecho original ilegível]" e não preencha com suposições (não tente adivinhar doses ou sintomas baseados em suposições).

PENSAMENTO PASSO A PASSO (Chain-of-Thought):
Antes de gerar o JSON, analise mentalmente o texto:
- Identifique jargões médicos e pense em sinônimos simples (Ex: "afecções do trato respiratório" -> "infecções na respiração, nariz ou garganta").
- Identifique trechos críticos de segurança para garantir transcrição exata.
- Formule a resposta simplificada.

EXEMPLO DE SIMPLIFICAÇÃO (Few-Shot):
Original (OCR): "O farmaco eh contraindicado em pctes com insuf. hepatica severa."
Simplificado: "Você não deve usar este medicamento se tiver problemas graves no fígado."

FORMATO DE SAÍDA:
Retorne EXCLUSIVAMENTE um objeto JSON válido (com aspas duplas nas chaves), SEM usar blocos de código Markdown (` ```json `), com as seguintes 11 chaves exatas:
"indicacao", "funcionamento", "contraindicacoes", "precaucoes_populacoes_especiais", "interacoes_medicamentosas", "armazenamento", "posologia_uso", "esquecimento", "efeitos_colaterais", "superdose", "avisos_seguranca".

TEXTO EXTRAÍDO PELO OCR:
{texto_bula}
"""

def montar_prompt_simplificacao(texto_bula: str) -> str:
    """Preenche o template com o texto da bula e retorna o prompt completo."""
    return PROMPT_SISTEMA_BULA.format(texto_bula=texto_bula)
