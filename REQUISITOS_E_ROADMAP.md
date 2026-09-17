# Projeto: Simplificação Automática de Textos de Saúde (Bulas de Medicamentos)

## 1. Requisitos do Projeto (Baseado no PDF)

### 1.1. Backend (Microsserviços)
- **Tecnologia:** Python com framework FastAPI.
- **Módulo de OCR:** Implementação obrigatória da biblioteca **EasyOCR** para extração de texto de fotos de bulas físicas.
- **Módulo de PLN/LLM:** Integração com APIs de LLMs (prioridade para Gemini família Flash).
- **Técnicas de Prompting:** Uso de **Few-Shot** e **Chain-of-Thought** para garantir simplificação textual para linguagem leiga, extraindo o conteúdo de acordo com a RDC nº 47/2009 da ANVISA (perguntas como "Para que serve?").

### 1.2. Frontend (Aplicativo Móvel)
- **Tecnologia:** Flutter.
- **Design:** Aplicação dos princípios do Design Universal para acessibilidade a usuários leigos.
- **Funcionalidades Core:**
  - Navegação temática guiada por perguntas simples.
  - Leitura do texto em áudio (**Text-to-Speech**).
  - **Agenda inteligente** com alarmes para os horários dos medicamentos.

### 1.3. Avaliação e Qualidade
- **Índice de Legibilidade:** Utilização do Índice de Legibilidade Flesch (adaptado ao português) para comparar o antes e o depois da simplificação.
- **Segurança da Informação:** Uso de algoritmos de similaridade semântica baseados em **embeddings** para garantir que a informação médica original não foi alterada, perdida ou alucinada.
- **Corpus de Referência:** Utilização de bulas da RENAME/Bulário Eletrônico da ANVISA.

---

## 2. Ordem Lógica de Desenvolvimento (Roadmap)

Abaixo apresento a sequência ideal para a construção do projeto, evoluindo do atual piloto para o produto final exigido:

### FASE 1: Adaptação e Melhoria do Pipeline Core (Python)
- [ ] **Passo 1.1 - Migração do OCR:** Substituir o Tesseract pelo EasyOCR no script de extração. O EasyOCR foi exigido devido à robustez em imagens não controladas e suporte nativo ao português.
- [ ] **Passo 1.2 - Engenharia de Prompts (LLM):** Modificar a comunicação com o Gemini. Sair do modo "corretor ortográfico" para o modo "simplificador". Implementar as técnicas de Few-Shot e Chain-of-Thought para gerar as respostas no formato leigo exigido pela ANVISA.
- [ ] **Passo 1.3 - Implementação das Métricas:** Desenvolver os scripts para calcular o Índice Flesch (em português) e o script de Similaridade Semântica por Embeddings para validar a qualidade da simplificação do LLM e evitar alucinações.

### FASE 2: Estruturação da API (Backend)
- [ ] **Passo 2.1 - Criação do FastAPI:** Desenvolver a estrutura base do FastAPI com rotas assíncronas.
- [ ] **Passo 2.2 - Integração OCR na API:** Transformar a lógica do EasyOCR em um endpoint (ex: recebendo o upload de uma imagem).
- [ ] **Passo 2.3 - Integração LLM na API:** Integrar o fluxo de simplificação via Gemini como um serviço consumido pelo endpoint da bula.

### FASE 3: Desenvolvimento do Aplicativo (Frontend)
- [ ] **Passo 3.1 - Estrutura Base Flutter:** Criar o projeto Flutter com arquitetura organizada (ex: BLoC ou Riverpod).
- [ ] **Passo 3.2 - Telas e Design Universal:** Implementar a UI guiada por perguntas de forma clara, acessível e responsiva.
- [ ] **Passo 3.3 - Integração Câmera e API:** Implementar a funcionalidade de tirar foto da bula, enviar para o backend e receber o texto simplificado.
- [ ] **Passo 3.4 - Text-to-Speech (TTS):** Implementar a leitura das respostas simplificadas em voz alta.
- [ ] **Passo 3.5 - Agenda Posológica:** Desenvolver funcionalidade local de notificações/alarmes para lembrar dos horários de medicação.

### FASE 4: Documentação e Publicação Acadêmica
- [ ] **Passo 4.1 - Análise Experimental:** Rodar as métricas em lote utilizando o corpus oficial de bulas para gerar os dados do relatório PIVIC.
- [ ] **Passo 4.2 - Escrita Científica:** Auxílio na redação dos artigos, documentando a eficácia técnica da aplicação para submissão em revistas da área.
