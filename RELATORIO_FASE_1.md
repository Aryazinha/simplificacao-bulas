# Revisão da Fase 1: Auditoria Médica por LLM (Cross-Evaluation)

Nesta etapa do projeto, focamos em resolver uma das maiores deficiências dos embeddings matemáticos na área da saúde: a **Fidelidade Clínica**.

Ao invés de depender puramente da similaridade de cosseno (que pode ignorar negações e falhar ao detectar erros numéricos críticos), desenvolvemos uma arquitetura **Actor-Critic**, onde um LLM atua como gerador (simplificador) e um LLM independente atua como **Auditor Médico Sênior**.

## O que foi construído?

Desenvolvemos três scripts diferentes no diretório `src/comparacao/` para garantir redundância e flexibilidade de infraestrutura:

1. [**`auditor_medico_openai.py`**](src/comparacao/auditor_medico_openai.py): Usa o `gpt-4o-mini` para uma validação em nuvem de altíssima precisão de raciocínio.
2. [**`auditor_medico_gemini.py`**](src/comparacao/auditor_medico_gemini.py): Usa o `gemini-3.6-flash`, servindo como alternativa gratuita via Google AI Studio. Descobrimos empiricamente que o Google aplica restrições pesadas de tráfego (*Error 503*) na camada gratuita, reforçando a necessidade de ambientes locais para sistemas médicos.
3. [**`auditor_medico_ollama.py`**](src/comparacao/auditor_medico_ollama.py): A "joia da coroa" do ponto de vista de privacidade médica. Utiliza o `llama3.2` rodando 100% offline, forçando a saída para um JSON estruturado.

> [!NOTE]
> Todos os auditores retornam estritamente o formato JSON para garantir fácil acoplamento na futura API (Fase 2):
> ```json
> {
>   "diagnosticos_mantidos": true,
>   "medicamentos_e_doses_exatos": false,
>   "sem_alucinacoes": true,
>   "aprovado": false,
>   "justificativa": "..."
> }
> ```

## Descoberta Crítica: Sensibilidade de Jargões Médicos

Durante os testes com o modelo local (Llama 3.2), identificamos um comportamento excessivamente rigoroso (*falso negativo*), onde a IA reprovava a tradução da bula caso houvesse mudança de caracteres no jargão, mesmo que a intenção clínica estivesse correta (ex: traduzir "8/8h" para "a cada 8 horas").

> [!IMPORTANT]
> **Engenharia de Prompt:** Tivemos que calibrar o *System Prompt* de todos os modelos, incluindo a regra explícita: 
> *"É permitido e desejável transformar termos médicos e jargões (como 8/8h) em linguagem comum (a cada 8 horas), desde que o significado clínico temporal não mude."*
> Essa alteração foi documentada com sucesso no [**`ACHADOS_ARTIGO.md`**](ACHADOS_ARTIGO.md).

## Definição de Escopo de Bancos de Dados

Também revisamos as restrições documentadas no [**`REQUISITOS_E_ROADMAP.md`**](REQUISITOS_E_ROADMAP.md) para garantir que a transição para a Fase 2 faça sentido arquiteturalmente:
- **Banco de Dados Estático (RAG):** Será carregado com o *Bulário Eletrônico da ANVISA*.
- **Banco de Dados Dinâmico:** Será essencial na API para salvar o progresso dos usuários e permitir a criação da *Agenda Inteligente* (alarmes no Flutter).

> [!TIP]
> Foi esclarecido que o projeto focará prioritariamente em **Bulas (documentos padronizados impressos)**, evitando os bloqueios massivos de leitura envolvidos no OCR de receitas médicas manuscritas.
